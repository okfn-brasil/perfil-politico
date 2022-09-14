from collections import namedtuple

from argparse import RawTextHelpFormatter
from django_bulk_update.helper import bulk_update
from django.db import connection
from django.db.utils import IntegrityError
from django.core.management import base
from logging import getLogger
from pathlib import Path
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.management.commands import CsvSlicer, get_city, get_party, parse_date
from perfil.core.models import Affiliation, Politician
from perfil.core.management.parties_map_2022 import parties

Row = namedtuple(
    "Row", (
        "partido",
        "nome",
        "uf",
        "municipio",
        "zona_eleitoral",
        "titulo_eleitoral",
        "data_filiacao",
        "situacao",
    )
)

class Command(base.BaseCommand):
    def create_parser(self, *args, **kwargs):
        """Allow multi-line help text"""
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("csv", help="Path to CSV file")

    help = (
        "Creates or updates political party affiliation data imported "
        "from Brasil.io: https://brasil.io/dataset/eleicoes-brasil/filiados"
    )
    model = Affiliation
    statuses = {
        value.upper().replace(" ", "_"): key for key, value in Affiliation.STATUSES
    }

    total_lines = 0

    #TODO document to delete and unlink politicians
    #Done create tmp table
    #Done insert into tmp table from csv
    #Update values that are in tmp table
    #Create values that are in tmp table but not in core_affiliations
    #Done? or create politicians
    #TODO link politicians

    def handle(self, *args, **options):
        self.log = getLogger(__name__)
        path = Path(options["csv"])
        if not path.exists():
            raise base.CommandError(f"{self.path} does not exist")

        self.drop_tmp_table()
        self.create_tmp_table()
        self.import_csv_data_to_tmp_table(path)

        updated_affiliations = self.update_affiliations()
        print(f"Updated {len(updated_affiliations)} Affiliations")

        created_affiliations = self.create_new_affiliations()
        print(f"Created {len(created_affiliations)} Affiliations")

        affiliations = updated_affiliations + created_affiliations
        print(f"Total Affiliations changed {len(affiliations)}")

        self.create_or_update_politicians_from_affiliations(affiliations)
        # self.delete_outdated_affiliations()
        # self.insert_from_tmp_table()

        # self.drop_tmp_table()

    def create_tmp_table(self):
        sql = """
            CREATE TABLE public.tmp_affiliation (
                id SERIAL primary key,
                partido character varying(127) NOT NULL,
                nome character varying(127) NOT NULL,
                uf character varying(7) NOT NULL,
                municipio character varying(127) NOT NULL,
                zona_eleitoral character varying(15) NOT NULL,
                titulo_eleitoral character varying(31) NOT NULL,
                data_filiacao character varying(31) NOT NULL,
                situacao character varying(31) NOT NULL
            );
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)

    def drop_tmp_table(self):
        sql = "DROP TABLE tmp_affiliation;"

        with connection.cursor() as cursor:
            cursor.execute(sql)

    def get_politicians_from_affiliations(self):
        pass

    def get_outdated_affiliations_new_values_dict(self):
        sql = """
            SELECT 
                A.id,
                B.partido,
                B.nome,
                B.uf,
                B.municipio,
                B.zona_eleitoral,
                B.titulo_eleitoral,
                B.data_filiacao,
                B.situacao
            FROM core_affiliation A
            INNER JOIN tmp_affiliation B
                ON A.voter_id = B.titulo_eleitoral 
                AND CAST(A.started_in AS VARCHAR) = B.data_filiacao
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            affiliations = Affiliation.objects.filter(id__in=(row[0] for row in rows))
            update_values = (Row(*row[1:]) for row in rows)
            return dict(zip(affiliations, update_values))

    def update_affiliations(self):
        affiliations_dict = self.get_outdated_affiliations_new_values_dict()
        for affiliation, values in affiliations_dict.items():
            self.set_affiliation_values(affiliation, values)

        affiliations = affiliations_dict.keys()
        bulk_update(affiliations)

        return tuple(affiliations)

    def get_new_affliation_rows(self):
        sql = """
        SELECT 
            B.partido,
            B.nome,
            B.uf,
            B.municipio,
            B.zona_eleitoral,
            B.titulo_eleitoral,
            B.data_filiacao,
            B.situacao
        FROM tmp_affiliation B
        LEFT JOIN core_affiliation A
            ON A.voter_id = B.titulo_eleitoral AND CAST(A.started_in AS VARCHAR) = B.data_filiacao
            WHERE A.id IS NULL
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return (Row(*row) for row in cursor.fetchall())

    def create_new_affiliations(self):
        row_values = self.get_new_affliation_rows()
        affiliations = tuple()
        for values in row_values:
            affiliations += (self.set_affiliation_values(Affiliation(), values),)

        self.model.objects.bulk_create(affiliations)
        return affiliations

    def import_csv_data_to_tmp_table(self, csv_path):
        with CsvSlicer(csv_path) as source:
            self.total_lines = source.total_lines
            kwargs = {
                "desc": f"Importing {self.model._meta.verbose_name} data into temporary table",
                "total": self.total_lines,
                "unit": "lines",
            }
            with tqdm(**kwargs) as progress_bar:
                for reader in source.basic_readers:
                    bulk = tuple(reader)
                    self.import_tmp_affiliation_bulk(bulk)
                    progress_bar.update(len(bulk))


    def import_tmp_affiliation_bulk(self, data):
        sql = f"""
            INSERT INTO tmp_affiliation(
                partido,
                nome,
                uf,
                municipio,
                zona_eleitoral,
                titulo_eleitoral,
                data_filiacao,
                situacao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
        with connection.cursor() as cursor:
            cursor.executemany(sql, data)

    # def delete_outdated_affiliations(self):
    #     sql = """
    #         DELETE
    #         FROM core_affiliation A
    #         USING tmp_affiliation B
    #         WHERE A.voter_id = B.titulo_eleitoral
    #             AND CAST(A.started_in AS VARCHAR) = B.data_filiacao;
    #     """
    #     with connection.cursor() as cursor:
    #         cursor.execute(sql)

    def insert_from_tmp_table(self):
        kwargs = {"desc": "Inserting data from temporary table", "total": self.total_lines, "unit": "rows"}
        rows = self.get_affiliation_rows()
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(rows, 4096):
                serialized_objs = tuple(self.serialize_row(row) for row in bulk)
                objs = (obj for obj in serialized_objs if isinstance(obj, self.model))
                self.model.objects.bulk_create(objs)
                progress_bar.update(len(bulk))

    def get_affiliation_rows(self):
        Row = namedtuple(
            "Row", (
                "partido",
                "nome",
                "uf",
                "municipio",
                "zona_eleitoral",
                "titulo_eleitoral",
                "data_filiacao",
                "situacao",
            )
        )
        sql = """
            SELECT
                partido,
                nome,
                uf,
                municipio,
                zona_eleitoral,
                titulo_eleitoral,
                data_filiacao,
                situacao
            FROM tmp_affiliation
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            yield from (Row(*row) for row in cursor.fetchall())

    def set_affiliation_values(self, affiliation, values):
        city = get_city(values.municipio, values.uf)
        party = get_party(parties[values.partido], values.partido)
        status = self.statuses.get(values.situacao)

        affiliation.name = values.nome
        affiliation.voter_id = values.titulo_eleitoral
        affiliation.started_in = values.data_filiacao
        affiliation.electoral_section = None
        affiliation.electoral_zone = values.zona_eleitoral
        affiliation.party = party
        affiliation.city = city
        affiliation.status = status
        affiliation.ended_in = None
        affiliation.canceled_in = None
        affiliation.regularized_in = None
        affiliation.processed_in = None
        affiliation.extracted_in = None
        affiliation.cancel_reason = ""

        return affiliation

    def create_or_update_politicians_from_affiliations(self, affiliations):
        affiliations_set = set(affiliations)
        politicians_to_update = Politician.objects.select_related("current_affiliation").filter(
            current_affiliation__in=affiliations_set,
        )
        # from ipdb import set_trace; set_trace()

        for politician in politicians_to_update:
            # politician.current_affiliation = self.get_current_affiliation(politician.current_affiliation.voter_id)
            # politician.affiliation_history = self.build_affiliation_history(politician.current_affiliation.voter_id)
            # politician.save()
            affiliations_set -= {politician.current_affiliation}

        # from ipdb import set_trace; set_trace()

        print(f"Updated {len(politicians_to_update)} Politicians")

        politicians_to_create = tuple()
        errors = []
        for affiliation in affiliations_set:
            politician = Politician(
                current_affiliation=affiliation,
                affiliation_history=self.build_affiliation_history(affiliation.voter_id),
            )
            politicians_to_create += (politician,)
            try:
                politician.save()
            except IntegrityError as e:
                errors += [e]

        print(errors)

        # Politician.objects.bulk_create(politicians_to_create)
        print(f"Created {len(politicians_to_create)} Politicians")

        from ipdb import set_trace;set_trace()

        return tuple(politicians_to_update) + politicians_to_create


    @staticmethod
    def get_current_affiliation(voter_id) -> Affiliation:
        return Affiliation.objects.filter(
            status=Affiliation.REGULAR,
            voter_id=voter_id,
        ).latest("started_in", "id")

    @staticmethod
    def build_affiliation_history(voter_id) -> list:
        affiliations = Affiliation.objects.filter(voter_id=voter_id).values_list(
            "party__abbreviation", "started_in"
        )
        return [
            {"party": party, "started_in": started_in.strftime("%Y-%m-%d")}
            for party, started_in in affiliations
        ]

    def politicians_from_affiliation(self):
        sql = """
            SELECT DISTINCT(voter_id)
            FROM core_affiliation
            WHERE status = 'R';
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            for voter_id, *_ in cursor.fetchall():
                current_affiliation = self.get_current_affiliation(voter_id)
                affiliation_history = self.build_affiliation_history(voter_id)
                yield Politician(
                    current_affiliation=current_affiliation,
                    affiliation_history=affiliation_history,
                )

    def post_handle(self):
        print(f"Deleted {self.delete_count} outdated affiliations")
        return
        # get most recent affiliation to create `Politician` instances
        total = (
            Affiliation.objects.filter(status=Affiliation.REGULAR)
            .values("voter_id")
            .distinct()
            .count()
        )
        kwargs = {
            "desc": f"Creating {Politician._meta.verbose_name} data with affiliation history",
            "total": total,
            "unit": "politicians",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(self.politicians_from_affiliation(), 8192):
                Politician.objects.bulk_create(bulk)
                progress_bar.update(len(bulk))

        self.drop_tmp_table()

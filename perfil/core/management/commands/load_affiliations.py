from collections import namedtuple

from django.db import connection
from django_bulk_update.helper import bulk_update
from tqdm import tqdm
from rows.plugins.utils import ipartition

from perfil.core.management.commands import BaseCommand, get_city, get_party, parse_date
from perfil.core.models import Affiliation, Politician

class Command(BaseCommand):

    help = (
        "Import political party affiliation data from Brasil.io: "
        "https://brasil.io/dataset/eleicoes-brasil/filiados"
    )
    model = Affiliation
    statuses = {
        value.upper().replace(" ", "_"): key for key, value in Affiliation.STATUSES
    }

    def serialize(self, line):
        city = get_city(line["codigo_municipio"], line["municipio"], line["uf"])
        party = get_party(line["sigla_partido"], line["partido"])
        status = self.statuses.get(line["situacao"])

        return Affiliation(
            cancel_reason=line["motivo_cancelamento"],
            canceled_in=parse_date(line["data_cancelamento"]),
            city=city,
            electoral_section=line["secao_eleitoral"],
            electoral_zone=line["zona_eleitoral"],
            ended_in=parse_date(line["data_desfiliacao"]),
            name=line["nome"],
            party=party,
            processed_in=parse_date(line["data_processamento"]),
            regularized_in=parse_date(line["data_regularizacao"]),
            started_in=line["data_filiacao"],
            status=status,
            voter_id=line["titulo_eleitoral"],
        )

    @staticmethod
    def politicians_from_affiliation():
        # TODO use the ORM (get most recent affiliation for each `voter_id`)
        sql = """
            SELECT core_affiliation.*
            FROM core_affiliation
            INNER JOIN (
                SELECT voter_id, MAX(started_in) AS started_in
                FROM core_affiliation
                GROUP BY voter_id
            ) AS most_recent
            ON most_recent.voter_id = core_affiliation.voter_id
            WHERE status = 'R';
        """
        yield from (
            Politician(current_affiliation=affiliation)
            for affiliation in Affiliation.objects.raw(sql).iterator()
        )

    @staticmethod
    def affiliations_per_politician():
        Row = namedtuple("Row", ("id", "started_in", "party"))
        print("Worry not: this query takes several minutes to run…")
        sql = """
            SELECT
                politician_voter.politician_id,
                party_voter.started_in,
                party_voter.abbreviation
            FROM (
                SELECT abbreviation, started_in, voter_id
                FROM core_affiliation
                INNER JOIN core_party
                ON core_affiliation.party_id = core_party.id
            ) party_voter
            INNER JOIN (
                SELECT core_politician.id AS politician_id, voter_id
                FROM core_politician
                INNER JOIN core_affiliation
                ON core_politician.current_affiliation_id = core_affiliation.id
            ) politician_voter
            ON politician_voter.voter_id = party_voter.voter_id
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            yield from (Row(*row) for row in cursor.fetchall())

    @staticmethod
    def serialize_bulk(bulk):
        # cache politicians organized by id to quickly retrieve them
        ids = set(row.id for row in bulk)
        politicians = {
            politician.id: politician
            for politician in Politician.objects.filter(id__in=ids)
        }

        # create asset history
        for row in bulk:
            politician = politicians.get(row.id)
            politician.affiliation_history.append(
                {"party": row.party, "started_in": row.started_in.strftime("%Y-%m-%d")}
            )

        yield from politicians.values()

    def post_handle(self):
        # get most recent affiliation to create `Politician` instances
        total = (
            Affiliation.objects.filter(status=Affiliation.REGULAR)
                .values("voter_id")
                .distinct()
                .count()
        )
        kwargs = {
            "desc": f"Importing {Politician._meta.verbose_name} data",
            "total": total,
            "unit": "politicians",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(self.politicians_from_affiliation(), 8192):
                Politician.objects.bulk_create(bulk)
                progress_bar.update(len(bulk))

        # get affiliafill in the `Politician.affiliation_history` field
        assets = tuple(self.affiliations_per_politician())
        kwargs = {
            "desc": f"Creating affiliation history per politician",
            "total": len(assets),
            "unit": "politicians",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(assets, 4096):
                bulk = tuple(self.serialize_bulk(bulk))
                bulk_update(bulk, update_fields=["affiliation_history"])
                progress_bar.update(len(bulk))

from tqdm import tqdm
from rows.plugins.utils import ipartition
from django.db import connection
from django.db.models.aggregates import Count
from django.contrib.postgres.aggregates import ArrayAgg

from perfil.core.management.commands import BaseCommand, get_city, get_party, parse_date, remove_extra_spaces
from perfil.core.models import Affiliation, Politician
from perfil.core.management.parties_map_2022 import parties


class Command(BaseCommand):

    help = (
        "Creates or updates political party affiliation data imported "
        "from Brasil.io: https://brasil.io/dataset/eleicoes-brasil/filiados"
    )
    model = Affiliation
    statuses = {
        value.upper().replace(" ", "_"): key for key, value in Affiliation.STATUSES
    }
    delete_count = 0
    create_count = 0

    def delete_outdated_affiliations(self, *, voter_id, started_in):
        objs_count, _ = Affiliation.objects.filter(voter_id=voter_id, started_in=started_in).delete()
        self.delete_count += objs_count

    def serialize(self, line):
        city = get_city(line["municipio"], line["uf"])
        party_name = remove_extra_spaces(line["partido"])
        party = get_party(parties[party_name], party_name)
        status = self.statuses.get(line["situacao"])
        canceled_in = line.get("data_cancelamento")
        ended_in = line.get("data_desfiliacao")
        processed_in = line.get("data_processamento")
        regularized_in = line.get("data_regularizacao")
        started_in = line["data_filiacao"]
        voter_id = line["titulo_eleitoral"]
        self.delete_outdated_affiliations(voter_id=voter_id, started_in=started_in)
        self.create_count += 1

        return Affiliation(
            cancel_reason=line.get("motivo_cancelamento", ""),
            canceled_in=parse_date(canceled_in) if canceled_in else None,
            city=city,
            electoral_section=line.get("secao_eleitoral"),
            electoral_zone=line["zona_eleitoral"],
            ended_in=parse_date(ended_in) if ended_in else None,
            name=line["nome"],
            party=party,
            processed_in=parse_date(processed_in) if processed_in else None,
            regularized_in=parse_date(regularized_in) if regularized_in else None,
            started_in=started_in,
            status=status,
            voter_id=voter_id,
        )

    @staticmethod
    def get_current_affiliation(voter_id) -> Affiliation:
        return Affiliation.objects.filter(
            status=Affiliation.REGULAR,
            voter_id=voter_id,
        ).latest("started_in")

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
            "desc": f"Importing {Politician._meta.verbose_name} data with affiliation history",
            "total": total,
            "unit": "politicians",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(self.politicians_from_affiliation(), 8192):
                Politician.objects.bulk_create(bulk)
                progress_bar.update(len(bulk))

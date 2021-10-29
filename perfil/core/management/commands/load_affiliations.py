from tqdm import tqdm
from rows.plugins.utils import ipartition
from django.db import connection

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
            electoral_section=line["secao_eleitoral"] or None,
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

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
    statuses = {value.upper(): key for key, value in Affiliation.STATUSES}

    def serialize(self, line):
        city = get_city(line["codigo_municipio"], line["nome_municipio"], line["uf"])
        party = get_party(line["sigla_partido"], line["nome_partido"])
        status = self.statuses.get(line["situacao_registro"])

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

    def post_handle(self):
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

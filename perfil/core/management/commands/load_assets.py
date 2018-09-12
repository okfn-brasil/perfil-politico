from collections import namedtuple

from django.db import connection
from django_bulk_update.helper import bulk_update
from tqdm import tqdm
from rows.plugins.utils import ipartition

from perfil.core.management.commands import (
    BaseCommand,
    get_candidate,
    parse_datetime,
    parse_integer,
)
from perfil.core.models import Asset, Politician


class Command(BaseCommand):

    help = (
        "Import candidate data from Brasil.io: "
        "https://brasil.io/dataset/eleicoes-brasil/bens_candidatos"
    )
    model = Asset

    def serialize(self, line):
        candidate = get_candidate(
            line["ano_eleicao"], line["sigla_uf"], line["numero_sequencial"]
        )

        if not candidate:
            self.log.warning(
                f"No candidate for year {line['ano_eleicao']}, state "
                f"{line['sigla_uf']} and sequential number "
                f"{line['numero_sequencial']}."
            )
            return None

        return Asset(
            candidate=candidate,
            value=line["valor"],
            category=line["descricao_tipo"],
            category_code=parse_integer(line["codigo_tipo"]),
            detail=line["detalhe"],
            order=parse_integer(line["numero_ordem"]),
            last_update=parse_datetime(
                f"{line['data_ultima_atualizacao']} {line['hora_ultima_atualizacao']}"
            ),
        )

    @staticmethod
    def assets_per_politician_per_year():
        # TODO use the ORM?
        Row = namedtuple("Row", ("politician_id", "year", "value"))
        sql = """
            SELECT
                core_candidate.politician_id,
                core_candidate.year,
                SUM(core_asset.value) AS total
            FROM core_asset
            INNER JOIN core_candidate
            ON core_candidate.id = core_asset.candidate_id
            WHERE core_candidate.politician_id IS NOT NULL
            GROUP BY core_candidate.politician_id, core_candidate.year
            ORDER BY core_candidate.year DESC
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            yield from (Row(*row) for row in cursor.fetchall())

    @staticmethod
    def serialize_bulk(bulk):
        # cache politicians organized by id to quickly retrieve them
        ids = set(row.politician_id for row in bulk)
        politicians = {
            politician.id: politician
            for politician in Politician.objects.filter(id__in=ids)
        }

        # create asset history
        for row in bulk:
            year, value = int(row.year), float(row.value)
            politician = politicians.get(row.politician_id)
            politician.asset_history.append({"year": year, "value": value})

        yield from politicians.values()

    def post_handle(self):
        assets = tuple(self.assets_per_politician_per_year())
        kwargs = {
            "desc": f"Calculating {Asset._meta.verbose_name} per year/politician",
            "total": len(assets),
            "unit": "politician",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(assets, 4096):
                bulk = tuple(self.serialize_bulk(bulk))
                bulk_update(bulk, update_fields=["asset_history"])
                progress_bar.update(len(bulk))

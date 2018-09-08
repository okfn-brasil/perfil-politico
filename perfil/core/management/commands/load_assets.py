from perfil.core.management.commands import BaseCommand, get_candidate, parse_datetime
from perfil.core.models import Asset


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
            category_code=line["codigo_tipo"],
            detail=line["detalhe"],
            order=line["numero_ordem"],
            last_update=parse_datetime(
                f"{line['data_ultima_atualizacao']} {line['hora_ultima_atualizacao']}"
            ),
        )

    def post_handle(self):
        pass

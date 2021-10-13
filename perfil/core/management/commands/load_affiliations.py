from perfil.core.management.commands import BaseCommand, get_city, get_party, parse_date
from perfil.core.models import Affiliation


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

    def post_handle(self):
        pass

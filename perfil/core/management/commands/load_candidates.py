from perfil.core.management.commands import (
    BaseCommand,
    get_city,
    get_party,
    parse_integer,
    parse_date,
)
from perfil.core.models import Candidate


class Command(BaseCommand):

    help = (
        "Import candidate data from Brasil.io: "
        "https://brasil.io/dataset/eleicoes-brasil/candidatos"
    )
    model = Candidate

    def serialize(self, line):
        city = get_city(
            line["codigo_municipio_nascimento"],
            line["municipio_nascimento"],
            line["sigla_unidade_federativa_nascimento"],
        )
        party = get_party(line["sigla_partido"], line["partido"])
        return Candidate(
            voter_id=line["titulo_eleitoral"],
            taxpayer_id=line["cpf"],
            date_of_birth=parse_date(line["data_nascimento"]),
            place_of_birth=city,
            gender=line["genero"],
            email=line["email"],
            age=line["idade_data_posse"],
            ethnicity=line["etnia"],
            ethnicity_code=line["codigo_etnia"],
            marital_status=line["estado_civil"],
            marital_status_code=line["codigo_estado_civil"],
            education=line["grau_instrucao"],
            education_code=line["codigo_grau_instrucao"],
            nationality=line["nacionalidade"],
            nationality_code=line["codigo_nacionalidade"],
            occupation=line["ocupacao"],
            occupation_code=line["codigo_ocupacao"],
            election=line["eleicao"],
            year=parse_integer(line["ano"]),
            state=line["sigla_unidade_federativa"],
            round=parse_integer(line["turno"]),
            post=line["cargo"],
            post_code=parse_integer(line["codigo_cargo"]),
            status=line["situacao_candidatura"],
            party=party,
            name=line["nome"],
            ballot_name=line["nome_urna"],
            number=parse_integer(line["numero_urna"]),
            sequential=line["numero_sequencial"],
            coalition_name=line["legenda"],
            coalition_description=line["composicao_legenda"],
            coalition_short_name=line["sigla_legenda"],
            max_budget=line["despesa_maxima_campanha"],
            round_result=line["totalizacao_turno"],
            round_result_code=parse_integer(line["codigo_totalizacao_turno"]),
        )

    def post_handle(self):
        pass

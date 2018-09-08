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
            line["nome_municipio_nascimento"],
            line["sigla_uf_nascimento"],
        )
        party = get_party(line["sigla_partido"], line["nome_partido"])
        return Candidate(
            voter_id=line["titulo_eleitoral"],
            taxpayer_id=line["cpf"],
            date_of_birth=parse_date(line["data_nascimento"]),
            place_of_birth=city,
            gender=line["descricao_genero"],
            email=line["email"],
            age=line["idade_data_posse"],
            ethinicity=line["descricao_cor_raca"],
            ethinicity_code=line["codigo_cor_raca"],
            marital_status=line["descricao_estado_civil"],
            marital_status_code=line["codigo_estado_civil"],
            education=line["descricao_grau_instrucao"],
            education_code=line["codigo_grau_instrucao"],
            nationality=line["descricao_nacionalidade"],
            nationality_code=line["codigo_nacionalidade"],
            occupation=line["descricao_ocupacao"],
            occupation_code=line["codigo_ocupacao"],
            election=line["descricao_eleicao"],
            year=parse_integer(line["ano_eleicao"]),
            state=line["sigla_uf"],
            round=parse_integer(line["numero_turno"]),
            post=line["descricao_cargo"],
            post_code=parse_integer(line["codigo_cargo"]),
            status=line["descricao_situacao_candidatura"],
            party=party,
            name=line["nome"],
            ballot_name=line["nome_urna"],
            number=parse_integer(line["numero_urna"]),
            sequential=line["numero_sequencial"],
            coalition_name=line["nome_legenda"],
            coalition_description=line["composicao_legenda"],
            coalition_short_name=line["sigla_legenda"],
            max_budget=line["despesa_maxima_campanha"],
            round_result=line["descricao_totalizacao_turno"],
            round_result_code=parse_integer(line["codigo_totalizacao_turno"]),
        )

    def post_handle(self):
        pass

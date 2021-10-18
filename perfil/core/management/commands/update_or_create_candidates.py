from django.forms.models import model_to_dict
from perfil.core.models import Candidate
from perfil.core.management.commands import (
    BaseCommand,
    get_city,
    get_party,
    parse_integer,
    parse_date,
)


class Command(BaseCommand):

    help = (
        "Import candidate data from Brasil.io: "
        "https://brasil.io/dataset/eleicoes-brasil/candidatos"
    )
    model = Candidate

    def get_candidate_if_exists(self, queryable_attrs):
        try:
            return self.model.objects.filter(**queryable_attrs).get()
        except self.model.MultipleObjectsReturned:
            print(
                f"Multiple objects returned for query: {queryable_attrs}. Changing only the first."
            )
            return self.model.objects.filter(**queryable_attrs).first()
        except self.model.DoesNotExist:
            pass

    def update_candidate_if_necessary(self, candidate, all_attrs):
        old_values = model_to_dict(candidate)
        fields_to_update = {}
        for attribute_name, new_value in all_attrs.items():
            if old_values.get(attribute_name) != new_value:
                fields_to_update[attribute_name] = new_value
        if fields_to_update:
            self.model.objects.filter(pk=candidate.pk).update(**fields_to_update)

    @staticmethod
    def _build_candidate_attributes(line):
        code_state_of_birth = (
            line["sigla_unidade_federativa_nascimento"]
            if line["sigla_unidade_federativa_nascimento"]
            and line["sigla_unidade_federativa_nascimento"] != "NAO DIVULGAVEL"
            else "ND"
        )
        city = get_city(
            line["codigo_municipio_nascimento"],
            line["municipio_nascimento"],
            code_state_of_birth,
        )
        party = get_party(line["sigla_partido"], line["partido"])

        queryable_attrs = {
            "year": parse_integer(line["ano"]),
            "party": party,
            "state": line["sigla_unidade_federativa"],
            "voter_id": line["titulo_eleitoral"],
            "round": parse_integer(line["turno"]),
            "post_code": parse_integer(line["codigo_cargo"]),
        }
        all_attrs = {
            **queryable_attrs,
            "taxpayer_id": line["cpf"],
            "date_of_birth": parse_date(line["data_nascimento"]),
            "place_of_birth": city,
            "gender": line["genero"],
            "email": line["email"],
            "age": line["idade_data_posse"],
            "ethnicity": line["etnia"],
            "ethnicity_code": line["codigo_etnia"],
            "marital_status": line["estado_civil"],
            "marital_status_code": line["codigo_estado_civil"],
            "education": line["grau_instrucao"],
            "education_code": line["codigo_grau_instrucao"],
            "nationality": line["nacionalidade"],
            "nationality_code": line["codigo_nacionalidade"],
            "occupation": line["ocupacao"],
            "occupation_code": line["codigo_ocupacao"],
            "election": line["eleicao"],
            "post": line["cargo"],
            "post_code": parse_integer(line["codigo_cargo"]),
            "status": line["situacao_candidatura"],
            "name": line["nome"],
            "ballot_name": line["nome_urna"],
            "number": parse_integer(line["numero_urna"]),
            "sequential": line["numero_sequencial"],
            "coalition_name": line["legenda"],
            "coalition_description": line["composicao_legenda"],
            "coalition_short_name": line["sigla_legenda"],
            "max_budget": line["despesa_maxima_campanha"],
            "round_result": line["totalizacao_turno"],
            "round_result_code": parse_integer(line["codigo_totalizacao_turno"]),
        }

        return queryable_attrs, all_attrs

    def serialize(self, line):
        queryable_attrs, all_attrs = self._build_candidate_attributes(line)

        candidate = self.get_candidate_if_exists(queryable_attrs)

        if not candidate:
            return self.model(**all_attrs)

        self.update_candidate_if_necessary(candidate, all_attrs)

    def post_handle(self):
        pass

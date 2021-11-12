from perfil.core.management.commands import BaseCommand
from perfil.core.models import ElectionIncomeStatement


class Command(BaseCommand):

    help = (
        "Import election income statements data from Brasil.io:\n"
        "- Make the setup from https://github.com/turicas/eleicoes-brasil \n"
        "- Run the 'python tse.py receita' command"
    )
    model = ElectionIncomeStatement

    def serialize(self, line):
        if not line["valor"] or not (line["numero_sequencial"] or line["cpf"]):
            return

        return ElectionIncomeStatement(
            year=line["ano"],
            value=line["valor"],
            accountant_sequential=line["numero_sequencial"],
            accountant_taxpayer_id=line["cpf"],
            vice_candidate_taxpayer_id=line["cpf_vice_candidato"],
            deputy_substitute_taxpayer_id=line["cpf_vice_suplente"],
            document_number=line["numero_documento"],
            receipt_number=line["numero_recibo"] or line["numero_recibo_eleitoral"],
            description=line["descricao"],
            donor_name=(
                line["doador"]
                or line["doador_originario"]
                or line["doador_originario_receita_federal"]
                or line["doador_receita_federal"]
            ),
            donor_taxpayer_id=(
                line["cpf_cnpj_doador"] or line["cpf_cnpj_doador_originario"]
            ),
            donor_economic_sector=(
                line["setor_economico_doador"]
                or line["setor_economico_doador_originario"]
            ),
            donor_economic_sector_code=line["codigo_setor_economico_doador"],
            additional_information={
                "date": line["data"],
                "accountant_candidature_number": line["numero_candidatura"],
                "donor_type": line["tipo"] or line["origem_receita"],
                "income_statement_type": line["tipo_prestacao_contas"],
                "income_statement_situation": line["situacao_cadastral"],
                "income_origin": line["origem_receita"],
                "income_nature": line["natureza_receita"],
                "resource_kind": line["especie_recurso"] or line["tipo_recurso"],
                "resource_source": line["fonte_recurso"],
            },
        )

    def post_handle(self):
        pass

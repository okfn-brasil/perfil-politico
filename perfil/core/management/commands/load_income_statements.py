from tqdm import tqdm
from django.db.models import Q
from perfil.core.management.commands import BaseCommand
from perfil.core.models import ElectionIncomeStatement, Candidate


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
            date=line["data"],
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
                line["doador_receita_federal"]
                or line["doador_originario_receita_federal"]
                or line["doador"]
                or line["doador_originario"]
            ),
            donor_taxpayer_id=(
                line["cpf_cnpj_doador"] or line["cpf_cnpj_doador_originario"]
            ),
            donor_economic_sector_code=line["codigo_setor_economico_doador"],
            additional_income_information={
                "accountant_candidature_number": line["numero_candidatura"],
                "donor_type": line["tipo"] or line["origem_receita"],
                "income_statement_type": line["tipo_prestacao_contas"],
                "income_statement_situation": line["situacao_cadastral"],
                "income_origin": line["origem_receita"],
                "income_nature": line["natureza_receita"],
                "resource_kind": line["especie_recurso"] or line["tipo_recurso"],
                "resource_source": line["fonte_recurso"],
                "donor_economic_sector_description": (
                    line["setor_economico_doador"]
                    or line["setor_economico_doador_originario"]
                ),
            },
        )

    def _get_electoral_income_history(self, candidate: Candidate) -> list:
        if candidate.sequential and candidate.taxpayer_id:
            income_statements = ElectionIncomeStatement.objects.filter(
                Q(accountant_sequential=candidate.sequential)
                | Q(accountant_taxpayer_id=candidate.taxpayer_id)
            )
        elif candidate.sequential:
            income_statements = ElectionIncomeStatement.objects.filter(
                accountant_sequential=candidate.sequential
            )
        elif candidate.taxpayer_id:
            income_statements = ElectionIncomeStatement.objects.filter(
                accountant_taxpayer_id=candidate.taxpayer_id
            )
        else:
            return []
        return sorted(
            [
                {
                    "year": int(statement.year),
                    "value": float(statement.value),
                    "donor_economic_sector": statement.donor_economic_sector,
                    "donor_economic_sector_code": statement.donor_economic_sector_code,
                    "donor_name": statement.donor_name,
                    "donor_taxpayer_id": statement.donor_taxpayer_id,
                }
                for statement in income_statements.all()
            ],
            key=lambda item: item["year"],
        )

    def _search_and_set_electoral_income_history(self, candidate: Candidate):
        income_history = self._get_electoral_income_history(candidate)
        if not income_history:
            return
        candidate.politician.electoral_income_history = income_history
        candidate.politician.save(update_fields=["electoral_income_history"])

    def post_handle(self):
        candidates_with_politicians = Candidate.objects.filter(
            politician__isnull=False
        ).filter(Q(taxpayer_id__isnull=False) | Q(sequential__isnull=False))
        kwargs = {
            "desc": f"Pre-processing electoral income history for politicians.",
            "total": candidates_with_politicians.count(),
            "unit": "objects",
        }
        counter = 0
        bulk_size = 1000
        with tqdm(**kwargs) as progress_bar:
            for candidate in candidates_with_politicians.iterator():
                # some politicians are repeated in more than one candidate
                # we don't need to reprocess the income history for them
                if not candidate.politician.electoral_income_history:
                    self._search_and_set_electoral_income_history(candidate)

                # update counter after some time in order to the prompt not to be frantically updating
                counter += 1
                if counter == bulk_size:
                    progress_bar.update(counter)
                    counter = 0
            progress_bar.update(counter)

import pytest

from perfil.core.models import ElectionIncomeStatement


@pytest.mark.django_db
def test_election_income_statement_repr():
    statement = ElectionIncomeStatement.objects.create(
        year=2021,
        value=123.46,
        accountant_sequential=123,
        donor_name="Empresas Maria",
    )
    assert "2021" in repr(statement)
    assert "123.46" in repr(statement)
    assert "123" in repr(statement)
    assert "Empresas Maria" in repr(statement)

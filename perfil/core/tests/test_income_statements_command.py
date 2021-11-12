from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import ElectionIncomeStatement


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "receita.csv"


@pytest.mark.django_db
def test_income_statements_are_created():
    call_command("load_income_statements", str(FIXTURE))
    assert 7 == ElectionIncomeStatement.objects.count()


@pytest.mark.django_db
def test_non_politician_identifiable_income_statements_are_not_created():
    call_command("load_income_statements", str(FIXTURE))
    total_objects = ElectionIncomeStatement.objects.filter(
        accountant_sequential__isnull=True, accountant_taxpayer_id__isnull=True
    ).count()
    assert total_objects == 0


@pytest.mark.django_db
def test_income_statements_without_price_value_are_not_created():
    call_command("load_income_statements", str(FIXTURE))
    assert 0 == ElectionIncomeStatement.objects.filter(value__isnull=True).count()

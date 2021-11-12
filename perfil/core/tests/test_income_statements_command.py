from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import ElectionIncomeStatement, Politician, Candidate

FIXTURE = [
    Path() / "perfil" / "core" / "tests" / "fixtures" / "receita.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
]


@pytest.mark.django_db
def test_income_statements_are_created():
    call_command("load_income_statements", str(FIXTURE[0]))
    assert 7 == ElectionIncomeStatement.objects.count()


@pytest.mark.django_db
def test_non_politician_identifiable_income_statements_are_not_created():
    call_command("load_income_statements", str(FIXTURE[0]))
    total_objects = ElectionIncomeStatement.objects.filter(
        accountant_sequential__isnull=True, accountant_taxpayer_id__isnull=True
    ).count()
    assert total_objects == 0


@pytest.mark.django_db
def test_income_statements_without_price_value_are_not_created():
    call_command("load_income_statements", str(FIXTURE[0]))
    assert 0 == ElectionIncomeStatement.objects.filter(value__isnull=True).count()


@pytest.mark.django_db
def test_electoral_income_history_from_politicians_are_populated():
    call_command("load_affiliations", str(FIXTURE[1]))
    call_command("load_candidates", str(FIXTURE[2]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[0]))

    assert Politician.objects.exclude(electoral_income_history__exact=[]).count() == 2


@pytest.mark.django_db
def test_electoral_income_history_for_politician_is_properly_populated():
    call_command("load_affiliations", str(FIXTURE[1]))
    call_command("load_candidates", str(FIXTURE[2]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[0]))

    politician = Candidate.objects.filter(sequential="70000625538").get().politician

    expected_history_size = 3
    assert len(politician.electoral_income_history) == expected_history_size

    assert all(
        [
            (income["year"] == 2018 and income["value"] == 1510.0)
            or (income["year"] == 2019 and income["value"] == 2000.0)
            or (income["year"] == 2020 and income["value"] == 1510.0)
            for income in politician.electoral_income_history
        ]
    )

    expected_income_keys = [
        "year",
        "value",
        "donor_name",
        "donor_taxpayer_id",
        "donor_economic_sector",
        "donor_economic_sector_code",
    ]
    assert all(
        [
            list(income.keys()) == expected_income_keys
            for income in politician.electoral_income_history
        ]
    )


@pytest.mark.django_db
def test_electoral_income_history_is_found_even_if_candidate_is_missing_taxpayer_id():
    call_command("load_affiliations", str(FIXTURE[1]))
    call_command("load_candidates", str(FIXTURE[2]))
    call_command("link_affiliations_and_candidates")
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    candidate.taxpayer_id = ""
    candidate.save()
    call_command("load_income_statements", str(FIXTURE[0]))

    politician = Candidate.objects.filter(id=candidate.id).get().politician

    expected_history_size = 1
    assert len(politician.electoral_income_history) == expected_history_size


@pytest.mark.django_db
def test_electoral_income_history_is_found_even_if_candidate_is_missing_sequential():
    call_command("load_affiliations", str(FIXTURE[1]))
    call_command("load_candidates", str(FIXTURE[2]))
    call_command("link_affiliations_and_candidates")
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    candidate.sequential = ""
    candidate.save()
    call_command("load_income_statements", str(FIXTURE[0]))

    politician = Candidate.objects.filter(id=candidate.id).get().politician

    expected_history_size = 3
    assert len(politician.electoral_income_history) == expected_history_size


@pytest.mark.django_db
def test_electoral_income_history_is_empty_if_candidate_is_missing_sequential_and_taxpayer_id():
    call_command("load_affiliations", str(FIXTURE[1]))
    call_command("load_candidates", str(FIXTURE[2]))
    call_command("link_affiliations_and_candidates")
    candidate = Candidate.objects.filter(taxpayer_id="37282522120").get()
    candidate.taxpayer_id = ""
    candidate.sequential = ""
    candidate.save()
    call_command("load_income_statements", str(FIXTURE[0]))

    politician = Candidate.objects.filter(id=candidate.id).get().politician

    assert politician.electoral_income_history == []

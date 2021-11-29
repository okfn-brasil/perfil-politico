from pathlib import Path

import pytest
from django.shortcuts import resolve_url
from django.core.management import call_command

from perfil.core.models import Candidate

FIXTURE = [
    Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "receita.csv",
]


@pytest.mark.django_db
def test_returns_404_when_candidate_does_not_exist(client):
    url = resolve_url("api_candidate_economic_bonds", 12300000)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_return_income_history_from_politician_when_exists(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    # When
    candidate_pk = Candidate.objects.filter(sequential="70000625538").get().id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_history = eval(response.content)["election_income_history"]
    assert len(returned_history) == 3


@pytest.mark.django_db
def test_fetches_income_history_if_candidate_does_not_have_politician(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    candidate.politician = None
    candidate.save()
    # When
    candidate_pk = candidate.id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_history = eval(response.content)["election_income_history"]
    assert len(returned_history) == 3

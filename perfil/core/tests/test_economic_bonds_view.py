import json
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
def test_properly_fetches_income_history(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    # When
    candidate_pk = candidate.id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_history = json.loads(response.content)["election_income_history"]
    assert len(returned_history) == 3

    list_of_expected_keys = [
        "year",
        "value",
        "donor_name",
        "donor_taxpayer_id",
        "donor_company_name",
        "donor_company_cnpj",
        "donor_economic_sector_code",
        "donor_secondary_sector_codes",
    ]
    for item in returned_history:
        assert list_of_expected_keys == list(item.keys())


@pytest.mark.django_db
def test_properly_fetches_companies_associated_with_politician(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    mocked_company = {
        "cnpj_raiz": "12345678",
        "cnpj_ordem": "0001",
        "cnpj_dv": "00",
        "nome_empresa": "Corporative Corporations",
        "cnae_principal": 1230,
        "cnae_secundaria": "123,234,345,456",
        "uf": "MG",
        "data_inicio_atividade": "2001/01/01",
        "data_entrada_sociedade": "2002/02/02",
    }
    candidate.owned_companies = [mocked_company, mocked_company]
    candidate.save()
    # When
    candidate_pk = candidate.id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_companies = json.loads(response.content)[
        "companies_associated_with_politician"
    ]
    assert len(returned_companies) == 2

    expected_company = {
        "cnpj": "12345678000100",
        "company_name": "Corporative Corporations",
        "main_cnae": "1230",
        "secondary_cnaes": "123,234,345,456",
        "uf": "MG",
        "foundation_date": "2001/01/01",
        "participation_start_date": "2002/02/02",
    }
    for item in returned_companies:
        assert expected_company == item


@pytest.mark.django_db
def test_income_history_is_fetched_when_candidate_has_no_sequential(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    candidate.sequential = ""
    candidate.save()
    # When
    candidate_pk = candidate.id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_history = json.loads(response.content)["election_income_history"]
    assert len(returned_history) == 3


@pytest.mark.django_db
def test_income_history_is_fetched_when_candidate_has_no_taxpayer_id(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    candidate.taxpayer_id = ""
    candidate.save()
    # When
    candidate_pk = candidate.id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_history = json.loads(response.content)["election_income_history"]
    assert len(returned_history) == 1


@pytest.mark.django_db
def test_income_history_is_empty_if_candidate_has_no_sequential_nor_taxpayer_id(client):
    # Given
    call_command("load_affiliations", str(FIXTURE[0]))
    call_command("load_candidates", str(FIXTURE[1]))
    call_command("link_affiliations_and_candidates")
    call_command("load_income_statements", str(FIXTURE[2]))
    candidate = Candidate.objects.filter(sequential="70000625538").get()
    candidate.sequential = ""
    candidate.taxpayer_id = ""
    candidate.save()
    # When
    candidate_pk = candidate.id
    url = resolve_url("api_candidate_economic_bonds", candidate_pk)
    response = client.get(url)
    # Then
    returned_history = json.loads(response.content)["election_income_history"]
    assert returned_history == []

from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Candidate, City, Party


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv"


@pytest.mark.django_db
def test_existing_candidates_are_updated():
    # Given
    party = Party.objects.create(
        name="PARTIDO PROGRESSISTA",
        abbreviation="PP",
    )
    existing_candidate = Candidate.objects.create(
        year=2018,
        party=party,
        state="DF",
        voter_id="014403110906",
        round=1,
        post_code=8,
        name="CLAUDIA SOUSA COSTA",
    )
    # When
    call_command("update_or_create_candidates", str(FIXTURE))
    # Then
    assert 3 == Candidate.objects.count()

    updated_candidate = Candidate.objects.filter(pk=existing_candidate.pk).get()
    assert existing_candidate.name == updated_candidate.name
    assert existing_candidate.year == updated_candidate.year
    assert existing_candidate.party == updated_candidate.party
    assert existing_candidate.voter_id == updated_candidate.voter_id
    assert existing_candidate.round == updated_candidate.round
    assert existing_candidate.post_code == updated_candidate.post_code
    assert existing_candidate.taxpayer_id != updated_candidate.taxpayer_id
    assert existing_candidate.date_of_birth != updated_candidate.date_of_birth
    assert existing_candidate.place_of_birth != updated_candidate.place_of_birth
    assert existing_candidate.gender != updated_candidate.gender
    assert existing_candidate.email != updated_candidate.email
    assert existing_candidate.age != updated_candidate.age


@pytest.mark.django_db
def test_non_existing_candidates_were_created():
    call_command("update_or_create_candidates", str(FIXTURE))
    assert 3 == Candidate.objects.count()

    candidate = Candidate.objects.get(taxpayer_id="10693471832")
    assert 2018 == candidate.year
    assert date(1968, 4, 2) == candidate.date_of_birth
    assert City.objects.get(name="COLINAS") == candidate.place_of_birth
    assert "FEMININO" == candidate.gender
    assert "KLLAUDHIA@HOTMAIL.COM" == candidate.email
    assert "50" == candidate.age

    assert "PARDA" == candidate.ethnicity
    assert "03" == candidate.ethnicity_code
    assert "SOLTEIRO(A)" == candidate.marital_status
    assert "1" == candidate.marital_status_code
    assert "SUPERIOR COMPLETO" == candidate.education
    assert "8" == candidate.education_code
    assert "BRASILEIRA NATA" == candidate.nationality
    assert "1" == candidate.nationality_code
    assert "PROFESSOR E INSTRUTOR DE FORMACAO PROFISSIONAL" == candidate.occupation
    assert "235" == candidate.occupation_code

    assert "ELEICOES GERAIS ESTADUAIS 2018" == candidate.election
    assert 2018 == candidate.year
    assert "DF" == candidate.state
    assert 1 == candidate.round
    assert "DEPUTADO DISTRITAL" == candidate.post
    assert "CADASTRADO" == candidate.status

    assert "PARTIDO PROGRESSISTA" == candidate.party.name
    assert "PROFESSORA CLAUDIA COSTA" == candidate.ballot_name
    assert 11114 == candidate.number
    assert "70000601690" == candidate.sequential
    assert "PARTIDO ISOLADO" == candidate.coalition_name
    assert "PP" == candidate.coalition_description
    assert "" == candidate.coalition_short_name
    assert "-1" == candidate.max_budget

    assert "ELEITO" == candidate.round_result
    assert -1 == candidate.round_result_code

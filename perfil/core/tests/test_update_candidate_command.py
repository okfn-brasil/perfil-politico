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
        sequential=70000601690,
    )
    # When
    call_command("update_or_create_candidates", str(FIXTURE))
    # Then
    assert 4 == Candidate.objects.count()

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
    assert 4 == Candidate.objects.count()

    candidate = Candidate.objects.get(taxpayer_id="69823871191")
    assert date(1978, 8, 12) == candidate.date_of_birth
    assert City.objects.get(name="BRASILIA") == candidate.place_of_birth
    assert "MASCULINO" == candidate.gender
    assert "ELEICOESGERAISDF2018@GMAIL.COM" == candidate.email
    assert "40" == candidate.age

    assert "PARDA" == candidate.ethnicity
    assert "03" == candidate.ethnicity_code
    assert "SOLTEIRO(A)" == candidate.marital_status
    assert "1" == candidate.marital_status_code
    assert "SUPERIOR COMPLETO" == candidate.education
    assert "8" == candidate.education_code
    assert "BRASILEIRA NATA" == candidate.nationality
    assert "1" == candidate.nationality_code
    assert "POLICIAL MILITAR" == candidate.occupation
    assert "233" == candidate.occupation_code

    assert "ELEICOES GERAIS ESTADUAIS 2018" == candidate.election
    assert 2018 == candidate.year
    assert "DF" == candidate.state
    assert 1 == candidate.round
    assert "DEPUTADO DISTRITAL" == candidate.post
    assert "CADASTRADO" == candidate.status

    assert "PARTIDO REPUBLICANO DA ORDEM SOCIAL" == candidate.party.name
    assert "FORLANGOV" == candidate.ballot_name
    assert 90999 == candidate.number
    assert "70000605601" == candidate.sequential
    assert "PARTIDO ISOLADO" == candidate.coalition_name
    assert "PROS" == candidate.coalition_description
    assert "" == candidate.coalition_short_name
    assert "-1" == candidate.max_budget

    assert "NAO ELEITO" == candidate.round_result
    assert -1 == candidate.round_result_code


@pytest.mark.django_db
def test_if_more_than_one_candidate_exists_the_command_does_not_crash():
    # Given
    party = Party.objects.create(
        name="PARTIDO PROGRESSISTA",
        abbreviation="PP",
    )
    Candidate.objects.create(
        year=2018,
        party=party,
        state="DF",
        voter_id="014403110906",
        round=1,
        post_code=8,
        name="CLAUDIA SOUSA COSTA duplicada",
        sequential=70000601690,
    )
    candidate_we_want_to_update = Candidate.objects.create(
        year=2018,
        party=party,
        state="DF",
        voter_id="014403110906",
        round=1,
        post_code=8,
        name="CLAUDIA SOUSA COSTA",
        sequential=70000601690,
    )
    # When
    call_command("update_or_create_candidates", str(FIXTURE))
    # Then
    assert 5 == Candidate.objects.count()

    updated_candidate = Candidate.objects.filter(
        pk=candidate_we_want_to_update.pk
    ).get()
    assert candidate_we_want_to_update.name == updated_candidate.name
    assert candidate_we_want_to_update.year == updated_candidate.year
    assert candidate_we_want_to_update.party == updated_candidate.party
    assert candidate_we_want_to_update.voter_id == updated_candidate.voter_id
    assert candidate_we_want_to_update.round == updated_candidate.round
    assert candidate_we_want_to_update.post_code == updated_candidate.post_code
    assert candidate_we_want_to_update.date_of_birth != updated_candidate.date_of_birth
    assert candidate_we_want_to_update.taxpayer_id != updated_candidate.taxpayer_id
    assert (
        candidate_we_want_to_update.place_of_birth != updated_candidate.place_of_birth
    )
    assert candidate_we_want_to_update.gender != updated_candidate.gender
    assert candidate_we_want_to_update.email != updated_candidate.email
    assert candidate_we_want_to_update.age != updated_candidate.age

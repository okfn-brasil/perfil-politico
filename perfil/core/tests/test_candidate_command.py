from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Candidate, City, Party


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv.xz"


@pytest.mark.django_db
def test_cities_were_created():
    call_command("load_candidates", str(FIXTURE))
    assert 3 == City.objects.count()

    first_city = City.objects.first()
    assert "BRASILIA" == first_city.name
    assert "DF" == first_city.state

    last_city = City.objects.last()
    assert "GOIANIA" == last_city.name
    assert "GO" == last_city.state


@pytest.mark.django_db
def test_parties_were_created():
    call_command("load_candidates", str(FIXTURE))
    assert 3 == Party.objects.count()

    first_party = Party.objects.first()
    assert "PARTIDO DA SOCIAL DEMOCRACIA BRASILEIRA" == first_party.name
    assert "PSDB" == first_party.abbreviation

    last_party = Party.objects.last()
    assert "PARTIDO REPUBLICANO DA ORDEM SOCIAL" == last_party.name
    assert "PROS" == last_party.abbreviation


@pytest.mark.django_db
def test_candidates_were_created():
    call_command("load_candidates", str(FIXTURE))
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

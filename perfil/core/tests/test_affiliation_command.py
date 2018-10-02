from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Affiliation, City, Party, Politician


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv"


@pytest.mark.django_db
def test_cities_were_created():
    call_command("load_affiliations", str(FIXTURE))
    assert 2 == City.objects.count()

    first_city = City.objects.first()
    assert "CURITIBA" == first_city.name
    assert "PR" == first_city.state
    assert 81051 == first_city.code

    last_city = City.objects.last()
    assert "TUBARAO" == last_city.name
    assert "SC" == last_city.state
    assert 83674 == last_city.code


@pytest.mark.django_db
def test_parties_were_created():
    call_command("load_affiliations", str(FIXTURE))
    assert 2 == Party.objects.count()

    first_party = Party.objects.first()
    assert "AVANTE" == first_party.name
    assert "AV" == first_party.abbreviation

    last_party = Party.objects.last()
    assert "PARTIDO PIRATA" == last_party.name
    assert "PP" == last_party.abbreviation


@pytest.mark.django_db
def test_affiliations_were_created():
    call_command("load_affiliations", str(FIXTURE))
    assert 3 == Affiliation.objects.count()

    first = Affiliation.objects.first()
    assert "MARCOS ANTONIO ROSA SILVA" == first.name
    assert "014403110906" == first.voter_id
    assert date(1999, 9, 30) == first.started_in
    assert 136 == first.electoral_section
    assert 99 == first.electoral_zone

    assert Party.objects.get(abbreviation="AV") == first.party
    assert City.objects.get(code=83674) == first.city
    assert Affiliation.REGULAR == first.status


@pytest.mark.django_db
def test_politicians_were_created():
    call_command("load_affiliations", str(FIXTURE))
    assert 2 == Politician.objects.count()

    last = Politician.objects.last()
    assert "MARCOS ANTONIO ROSA SILVA" == last.current_affiliation.name
    assert "014403110906" == last.current_affiliation.voter_id
    assert date(1999, 9, 30) == last.current_affiliation.started_in
    assert 136 == last.current_affiliation.electoral_section
    assert 99 == last.current_affiliation.electoral_zone

    assert Party.objects.get(abbreviation="AV") == last.current_affiliation.party
    assert City.objects.get(code=83674) == last.current_affiliation.city
    assert last.affiliation_history == [
        {"party": "PP", "started_in": "2003-10-02"},
        {"party": "AV", "started_in": "1999-09-30"},
    ]

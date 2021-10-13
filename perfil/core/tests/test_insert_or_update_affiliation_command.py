from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Affiliation, City, Party


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv"


@pytest.mark.django_db
def test_cities_were_created():
    call_command("insert_or_update_affiliations", str(FIXTURE))
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
    call_command("insert_or_update_affiliations", str(FIXTURE))
    assert 2 == Party.objects.count()

    first_party = Party.objects.first()
    assert "AVANTE" == first_party.name
    assert "AV" == first_party.abbreviation

    last_party = Party.objects.last()
    assert "PARTIDO PIRATA" == last_party.name
    assert "PP" == last_party.abbreviation


@pytest.mark.django_db
def test_affiliations_were_created():
    call_command("insert_or_update_affiliations", str(FIXTURE))
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
def test_existing_affiliation_is_updated():
    # Given
    party = Party.objects.create(
        name="PARTIDO PIRATA",
        abbreviation="PP",
    )
    city = City.objects.create(
        code=81051,
        name="CURITIBA",
        state="PR",
    )
    Affiliation(
        name="MARCOS ANTONIO ROSA SILVA",
        voter_id="014403110906",
        started_in="2003-10-02",
        electoral_zone=12,
        party=party,
        city=city,
        status="R",
    ).save()

    # When
    call_command("insert_or_update_affiliations", str(FIXTURE))

    # Assert
    assert 3 == Affiliation.objects.count()

    # existing row is updated properly
    updated_affiliation = Affiliation.objects.filter(voter_id="014403110906", started_in="2003-10-02").get()
    assert "MARCOS ANTONIO ROSA SILVA" == updated_affiliation.name
    assert "Motivo" == updated_affiliation.cancel_reason
    assert date(2017, 2, 8) == updated_affiliation.ended_in
    assert Affiliation.EXCLUDED == updated_affiliation.status

    # non existing row is added properly
    new_affiliation = Affiliation.objects.filter(voter_id="014403110906", started_in="1999-09-30").get()
    assert "MARCOS ANTONIO ROSA SILVA" == new_affiliation.name
    assert Party.objects.get(abbreviation="AV") == new_affiliation.party
    assert Affiliation.REGULAR == new_affiliation.status

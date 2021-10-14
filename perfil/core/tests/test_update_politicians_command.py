from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import City, Party, Politician, Affiliation

FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv"


@pytest.mark.django_db
def test_politicians_were_created():
    # Given
    call_command("load_affiliations", str(FIXTURE))

    # When
    call_command("update_politicians")

    # Then
    assert 2 == Politician.objects.count()

    last = Politician.objects.last()
    assert "MARCOS ANTONIO ROSA SILVA" == last.current_affiliation.name
    assert "014403110906" == last.current_affiliation.voter_id
    assert date(1999, 9, 30) == last.current_affiliation.started_in
    assert 136 == last.current_affiliation.electoral_section
    assert 99 == last.current_affiliation.electoral_zone

    assert Party.objects.get(abbreviation="AV") == last.current_affiliation.party
    assert City.objects.get(code=83674) == last.current_affiliation.city

    affiliations = (
        {"party": "AV", "started_in": "1999-09-30"},
        {"party": "PP", "started_in": "2003-10-02"},
    )
    for affiliation in affiliations:
        assert affiliation in last.affiliation_history


@pytest.mark.django_db
def test_existing_politicians_are_not_updated_if_set_to_ignore_existing_politicians():
    # Given
    call_command("load_affiliations", str(FIXTURE))
    old_affiliation = Affiliation.objects.filter(
        voter_id="014403110906", status="D"
    ).get()
    Politician(current_affiliation=old_affiliation).save()

    # When
    call_command("update_politicians", ignore_existing_politicians=True)

    # Then
    assert 3 == Politician.objects.count()


@pytest.mark.django_db
def test_existing_politicians_were_updated():
    # Given
    call_command("load_affiliations", str(FIXTURE))
    politician_voter_id = "014403110906"
    old_affiliation = Affiliation.objects.filter(
        voter_id=politician_voter_id, status="D"
    ).get()
    Politician(current_affiliation=old_affiliation).save()
    # When
    call_command("update_politicians")

    # Then
    assert 2 == Politician.objects.count()

    new_affiliation = Affiliation.objects.filter(
        voter_id=politician_voter_id, status="R"
    ).get()
    politician = Politician.objects.filter(
        current_affiliation__voter_id=politician_voter_id
    ).get()
    assert politician.current_affiliation == new_affiliation

    affiliations = (
        {"party": "AV", "started_in": "1999-09-30"},
        {"party": "PP", "started_in": "2003-10-02"},
    )
    for affiliation in affiliations:
        assert affiliation in politician.affiliation_history

from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Politician


FIXTURES = (
    Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
)


@pytest.mark.django_db
def test_election_history_was_created():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    call_command("link_affiliations_and_candidates")
    call_command("link_politicians_and_election_results")

    first = Politician.objects.first()
    assert first.election_history == []

    last = Politician.objects.last()
    assert last.election_history == [
        {
            "post": "DEPUTADO DISTRITAL",
            "year": 2018,
            "result": "NAO ELEITO",
            "elected": False,
        },
        {
            "post": "DEPUTADO DISTRITAL",
            "year": 2018,
            "result": "ELEITO",
            "elected": True,
        },
    ]

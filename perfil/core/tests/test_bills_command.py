from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.management.commands.load_bills import get_politician
from perfil.core.models import Bill, Candidate, Politician


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "senado.csv"


def test_get_politician(candidates):
    assert get_politician("42") is None
    candidate = Candidate.objects.first()

    candidate.name = "MARIA AUXILIADORA SEABRA REZENDE"
    candidate.ballot_name = "PROFESSORA DORINHA"
    candidate.post = "SENADORA"
    candidate.save()
    assert (
        get_politician("PROFESSORA DORINHA SEABRA REZENDE", post="SENADORA")
        == candidate.politician
    )

    candidate.name = "DELCIDIO DO AMARAL GOMEZ"
    candidate.ballot_name = "DELCIDIO"
    candidate.save()
    assert get_politician("DELCIDIO DO AMARAL") == candidate.politician

    candidate.name = "RANDOLPH FREDERICH RODRIGUES ALVES"
    candidate.ballot_name = "RANDOLFE"
    candidate.save()
    assert get_politician("RANDOLFE RODRIGUES") == candidate.politician

    candidate.name = "LILIAM SA DE PAULA"
    candidate.ballot_name = "LILIAM SA"
    candidate.post = "SENADORA"
    candidate.save()
    assert get_politician("LILIAM SA DE PAULA", post="SENADORA") == candidate.politician


@pytest.mark.django_db
def test_bills_are_created(candidates):
    call_command("link_politicians_and_election_results")
    call_command("load_bills", str(FIXTURE))
    assert 4 == Bill.objects.count()


@pytest.mark.django_db
def test_authorship_are_linked(candidates):
    call_command("link_politicians_and_election_results")
    call_command("load_bills", str(FIXTURE))
    for politician in Politician.objects.all():
        assert 1 == politician.bills.count()

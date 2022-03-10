from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Politician, Candidate

FIXTURES = (
    Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
)


@pytest.mark.django_db
def test_politicians_are_removed():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    call_command("link_affiliations_and_candidates")
    call_command("unlink_and_delete_politician_references")
    assert Politician.objects.count() == 0


@pytest.mark.django_db
def test_command_does_not_crash_without_politicians_to_remove():
    call_command("unlink_and_delete_politician_references")
    assert Politician.objects.count() == 0


@pytest.mark.django_db
def test_candidates_are_preserved_without_politicians():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    call_command("link_affiliations_and_candidates")
    call_command("unlink_and_delete_politician_references")
    assert Candidate.objects.count() == 4
    assert Candidate.objects.filter(politician__isnull=False).count() == 0

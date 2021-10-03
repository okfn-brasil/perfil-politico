from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Politician


FIXTURES = (
    Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
)


@pytest.mark.django_db
def test_politicians_were_created():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    call_command("link_affiliations_and_candidates")
    assert 2 == Politician.objects.exclude(current_affiliation=None).count()

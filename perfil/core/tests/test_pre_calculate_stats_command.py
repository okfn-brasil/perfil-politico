from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import PreCalculatedStats

FIXTURES = (
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "bemdeclarado.csv",
)


@pytest.mark.django_db
def test_command_properly_store_calculated_stats():
    call_command("load_candidates", str(FIXTURES[0]))
    call_command("load_assets", str(FIXTURES[1]))
    call_command("pre_calculate_stats")

    assert PreCalculatedStats.objects.count() == 2

    assert PreCalculatedStats.objects.filter(year=2018).get().value == 80000
    assert float(PreCalculatedStats.objects.filter(year=2016).get().value) == 40900.87

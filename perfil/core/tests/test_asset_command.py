from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Asset, Candidate


FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "bemdeclarado.csv"


@pytest.mark.django_db
def test_assets_were_created(candidates):
    call_command("load_assets", str(FIXTURE))
    assert 3 == Asset.objects.count()

    asset = Asset.objects.get(category_code=13)
    assert Candidate.objects.get(sequential="70000625538") == asset.candidate
    assert Decimal("100000.00") == asset.value
    assert "TERRENO" == asset.category
    assert "" == asset.detail
    assert 4 == asset.order

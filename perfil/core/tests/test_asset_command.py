from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Asset, Candidate, Party

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

    candidate = Candidate.objects.get(sequential="70000625538")
    assert candidate.asset_history() == [{"year": 2018, "value": 400000.0}]


@pytest.mark.django_db
def test_assets_are_not_deleted_before_new_ones_are_created(candidates):
    # Given
    mock_party = Party.objects.create()
    mock_candidate = Candidate.objects.create(year=2020, state="SP", round=1, post_code=0, party=mock_party)
    Asset(candidate=mock_candidate).save()
    Asset(candidate=mock_candidate).save()
    # When
    call_command("load_assets", str(FIXTURE))  # without --clean-previous-data flag
    # Then
    assert 5 == Asset.objects.count()


@pytest.mark.django_db
def test_assets_are_deleted_before_new_ones_are_created(candidates):
    # Given
    mock_party = Party.objects.create()
    mock_candidate = Candidate.objects.create(year=2020, state="SP", round=1, post_code=0, party=mock_party)
    Asset(candidate=mock_candidate).save()
    # When
    call_command("load_assets", str(FIXTURE), "--clean-previous-data")
    # Then
    assert 3 == Asset.objects.count()

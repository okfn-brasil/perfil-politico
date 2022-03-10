from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.models import Asset, Candidate, Party

FIXTURE = Path() / "perfil" / "core" / "tests" / "fixtures" / "bemdeclarado.csv"


@pytest.mark.django_db
def test_models_are_not_deleted_before_new_ones_are_created(candidates):
    # Given
    mock_party = Party.objects.create()
    mock_candidate = Candidate.objects.create(
        year=2020, state="SP", round=1, post_code=0, party=mock_party
    )
    Asset(candidate=mock_candidate).save()
    Asset(candidate=mock_candidate).save()
    # When
    call_command("load_assets", str(FIXTURE))  # without clean-previous-data flag
    # Then
    assert 5 == Asset.objects.count()


@pytest.mark.django_db
def test_models_are_deleted_before_new_ones_are_created(candidates):
    # Given
    mock_party = Party.objects.create()
    mock_candidate = Candidate.objects.create(
        year=2020, state="SP", round=1, post_code=0, party=mock_party
    )
    Asset(candidate=mock_candidate).save()
    # When
    call_command("load_assets", str(FIXTURE), "clean-previous-data")
    # Then
    assert 3 == Asset.objects.count()


@pytest.mark.django_db
def test_command_works_even_when_there_is_no_previous_data(candidates):
    # Given
    # there is no "Asset" in the database
    # When
    call_command("load_assets", str(FIXTURE), "clean-previous-data")
    # Then
    assert 3 == Asset.objects.count()  # assets are properly created

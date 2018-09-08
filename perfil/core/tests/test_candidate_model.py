import pytest

from perfil.core.models import Candidate


@pytest.mark.django_db
def test_campaign_manager(candidates):
    assert 2 == Candidate.objects.campaign(2018).count()


@pytest.mark.django_db
def test_candidate_repr(candidates):
    candidate = Candidate.objects.first()
    assert candidate.ballot_name in repr(candidate)
    assert candidate.state in repr(candidate)
    assert candidate.politician.current_affiliation.party.abbreviation in repr(
        candidate
    )


@pytest.mark.django_db
def test_valid_image_property(candidates):
    candidate = Candidate.objects.first()
    candidate.state = "SC"
    candidate.sequential = "42"
    candidate.save()
    expected = (
        "https://serenata-de-amor-data.nyc3.digitaloceanspaces.com/"
        "perfil-politico/SC/42.jpg"
    )
    assert expected == candidate.image()


@pytest.mark.django_db
def test_invalid_image_property(candidates):
    candidate = Candidate.objects.last()
    assert candidate.image() is None

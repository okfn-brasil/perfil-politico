from datetime import date

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
def test_valid_image_method(candidates):
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
def test_invalid_image_method(candidates):
    candidate = Candidate.objects.last()
    assert candidate.image() is None


@pytest.mark.django_db
def test_valid_asset_history_method(candidates):
    candidate = Candidate.objects.last()
    candidate.politician.asset_history = [
        {"year": 2018, "value": 42.0},
        {"year": 2014, "value": 21.0},
    ]
    assert candidate.asset_history() == [
        {"year": 2014, "value": 21.0},
        {"year": 2018, "value": 42.0},
    ]


@pytest.mark.django_db
def test_invalid_asset_history_method(candidates):
    candidate = Candidate.objects.last()
    candidate.politician = None
    assert candidate.asset_history() == []


@pytest.mark.django_db
def test_valid_affiliation_history_method(candidates):
    candidate = Candidate.objects.last()
    candidate.politician.affiliation_history = [
        {"party": "AV", "started_in": "2018-01-02"},
        {"party": "PP", "started_in": "2010-09-07"},
    ]
    assert candidate.affiliation_history() == [
        {"party": "PP", "started_in": "2010-09-07"},
        {"party": "AV", "started_in": "2018-01-02"},
    ]


@pytest.mark.django_db
def test_invalid_affiliation_history_method(candidates):
    candidate = Candidate.objects.last()
    candidate.politician = None
    assert candidate.affiliation_history() == []


@pytest.mark.django_db
def test_valid_bill_keywords_method(candidates):
    candidate = Candidate.objects.last()
    candidate.politician.bill_keywords = [
        {"keyword": "bar", "total": 1},
        {"keyword": "foo", "total": 2},
    ]
    assert candidate.bill_keywords() == [
        {"keyword": "foo", "total": 2},
        {"keyword": "bar", "total": 1},
    ]


@pytest.mark.django_db
def test_invalid_bill_keywords_method(candidates):
    candidate = Candidate.objects.last()
    candidate.politician = None
    assert candidate.bill_keywords() == []


@pytest.mark.django_db
def test_get_age(candidates):
    candidate = Candidate.objects.last()

    candidate.age = 42
    assert 42 == candidate.get_age()

    candidate.age = None
    candidate.date_of_birth = None
    assert candidate.get_age() is None

    candidate.year = 1970
    candidate.age = None
    candidate.date_of_birth = date(1960, 2, 2)
    assert 10 == candidate.get_age()

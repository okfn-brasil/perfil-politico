from datetime import date

import pytest
from django.http import Http404, HttpResponse
from django.shortcuts import resolve_url

from perfil.core.views import Stats


def test_validate_argument():
    assert Stats.validate_argument("foo", {"foo", "bar"}) is None
    with pytest.raises(Http404):
        assert Stats.validate_argument("foobar", {"foo", "bar"})


def test_national_stats_instance(mocker):
    mock = mocker.patch.object(Stats, "validate_argument")
    stats = Stats(2018, "deputado-federal", "Ethnicity")
    assert 2 == mock.call_count
    assert 2018 == stats.year
    assert "DEPUTADO FEDERAL" == stats.post
    assert "ethnicity" == stats.characteristic
    assert stats.state is None


def test_state_stats_instance(mocker):
    mock = mocker.patch.object(Stats, "validate_argument")
    stats = Stats(2018, "deputado-federal", "Ethnicity", "sc")
    assert 3 == mock.call_count
    assert 2018 == stats.year
    assert "DEPUTADO FEDERAL" == stats.post
    assert "ethnicity" == stats.characteristic
    assert "SC" == stats.state


@pytest.mark.django_db
def test_age_stats_instance(mocker):
    mock = mocker.patch.object(Stats, "age_stats")
    mock.return_value = {}
    stats = Stats(2018, "deputado-federal", "age")
    assert stats.field == "date_of_birth"
    stats()
    mock.assert_called_once()


def test_party_stats_instance(mocker):
    stats = Stats(2018, "deputado-federal", "party")
    assert stats.field == "party__abbreviation"


@pytest.mark.django_db
def test_stats_call(mocker):
    response = mocker.patch("perfil.core.views.JsonResponse")
    stats = Stats(2018, "deputado-federal", "Ethnicity", "sc")
    stats()
    response.assert_called_once()


def test_national_stats_view(client, mocker):
    stats = mocker.patch("perfil.core.views.Stats")
    stats.return_value = HttpResponse
    url = resolve_url("api_national_stats", 2018, "deputado-federal", "age")
    client.get(url)
    stats.assert_called_once_with(2018, "deputado-federal", "age")


def test_state_stats_view(client, mocker):
    stats = mocker.patch("perfil.core.views.Stats")
    stats.return_value = HttpResponse
    url = resolve_url("api_state_stats", "sc", 2018, "deputado-federal", "age")
    client.get(url)
    stats.assert_called_once_with(2018, "deputado-federal", "age", "sc")


def test_age_stats_method():
    stats = Stats(2018, "deputado-federal", "age")
    data = (
        {"characteristic": date(1940, 1, 1), "total": 1},
        {"characteristic": date(1950, 1, 1), "total": 1},
        {"characteristic": date(1970, 1, 1), "total": 2},
        {"characteristic": date(1970, 1, 1), "total": 2},
        {"characteristic": date(1980, 1, 1), "total": 1},
        {"characteristic": date(1994, 1, 1), "total": 1},
        {"characteristic": date(1999, 1, 1), "total": 2},
    )
    expected = (
        {"characteristic": "less-than-25", "total": 2},
        {"characteristic": "between-25-and-34", "total": 1},
        {"characteristic": "between-35-and-44", "total": 1},
        {"characteristic": "between-45-and-59", "total": 4},
        {"characteristic": "between-60-and-69", "total": 1},
        {"characteristic": "70-or-more", "total": 1},
    )
    assert expected == stats.age_stats(data)

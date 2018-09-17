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


def test_stats_call(mocker):
    mocker.patch("perfil.core.views.connection")
    response = mocker.patch("perfil.core.views.JsonResponse")
    stats = Stats(2018, "deputado-federal", "Ethnicity")
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

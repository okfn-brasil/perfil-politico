from datetime import date
from pathlib import Path

import pytest
from django.http import Http404, HttpResponse
from django.shortcuts import resolve_url
from django.core.management import call_command

from perfil.core.models import PreCalculatedStats
from perfil.core.views import Stats, CandidateCharacteristicsStats, AssetStats


def test_validate_argument():
    assert Stats.validate_argument("foo", {"foo", "bar"}) is None
    with pytest.raises(Http404):
        assert Stats.validate_argument("foobar", {"foo", "bar"})


def test_validate_arguments():
    assert Stats.validate_arguments([], {"foo", "bar"}) is None
    assert Stats.validate_arguments(["foo", "bar"], {"foo", "bar"}) is None
    with pytest.raises(Http404):
        assert Stats.validate_arguments(["foo", "foobar"], {"foo", "bar"})


def test_national_stats_instance(mocker):
    mock = mocker.patch.object(CandidateCharacteristicsStats, "validate_argument")
    stats = CandidateCharacteristicsStats(2018, "deputado-federal", "Ethnicity")
    assert 2 == mock.call_count
    assert 2018 == stats.year
    assert "DEPUTADO FEDERAL" == stats.post
    assert "ethnicity" == stats.characteristic
    assert stats.state is None


def test_state_stats_instance(mocker):
    mock = mocker.patch.object(CandidateCharacteristicsStats, "validate_argument")
    stats = CandidateCharacteristicsStats(2018, "deputado-federal", "Ethnicity", "sc")
    assert 3 == mock.call_count
    assert 2018 == stats.year
    assert "DEPUTADO FEDERAL" == stats.post
    assert "ethnicity" == stats.characteristic
    assert "SC" == stats.state


@pytest.mark.django_db
def test_age_stats_instance(mocker):
    mock = mocker.patch.object(CandidateCharacteristicsStats, "age_stats")
    mock.return_value = {}
    stats = CandidateCharacteristicsStats(2018, "deputado-federal", "age")
    assert stats.field == "date_of_birth"
    stats()
    mock.assert_called_once()


def test_party_stats_instance(mocker):
    stats = CandidateCharacteristicsStats(2018, "deputado-federal", "party")
    assert stats.field == "party__abbreviation"


@pytest.mark.django_db
def test_stats_call(mocker):
    response = mocker.patch("perfil.core.views.JsonResponse")
    stats = CandidateCharacteristicsStats(2018, "deputado-federal", "Ethnicity", "sc")
    stats()
    response.assert_called_once()


def test_national_stats_view(client, mocker):
    stats = mocker.patch("perfil.core.views.CandidateCharacteristicsStats")
    stats.return_value = HttpResponse
    url = resolve_url("api_national_stats", 2018, "deputado-federal", "age")
    client.get(url)
    stats.assert_called_once_with(2018, "deputado-federal", "age")


def test_state_stats_view(client, mocker):
    stats = mocker.patch("perfil.core.views.CandidateCharacteristicsStats")
    stats.return_value = HttpResponse
    url = resolve_url("api_state_stats", "sc", 2018, "deputado-federal", "age")
    client.get(url)
    stats.assert_called_once_with(2018, "deputado-federal", "age", "sc")


def test_assets_stats_view_without_filters(client, mocker):
    stats = mocker.patch("perfil.core.views.AssetStats")
    stats.return_value = HttpResponse
    client.get(resolve_url("api_asset_stats"))
    stats.assert_called_once_with(states=[], posts=[])


def test_assets_stats_view_with_states_filter(client, mocker):
    stats = mocker.patch("perfil.core.views.AssetStats")
    stats.return_value = HttpResponse
    client.get(f"{resolve_url('api_asset_stats')}?state=MG")
    stats.assert_called_once_with(states=["MG"], posts=[])


def test_assets_stats_view_with_candidate_post_filter(client, mocker):
    stats = mocker.patch("perfil.core.views.AssetStats")
    stats.return_value = HttpResponse
    client.get(f"{resolve_url('api_asset_stats')}?candidate_post=some_post")
    stats.assert_called_once_with(states=[], posts=["some_post"])


def test_assets_stats_view_with_all_filters(client, mocker):
    stats = mocker.patch("perfil.core.views.AssetStats")
    stats.return_value = HttpResponse
    client.get(
        f"{resolve_url('api_asset_stats')}?state=MG&state=SP&candidate_post=vereador"
    )
    stats.assert_called_once_with(states=["MG", "SP"], posts=["vereador"])


def test_age_stats_method():
    stats = CandidateCharacteristicsStats(2018, "deputado-federal", "age")
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


@pytest.mark.django_db
def test_assets_stats_method_get_pre_calculated_stats_when_no_filter_is_used(mocker):
    # Given
    response = mocker.patch("perfil.core.views.JsonResponse")
    PreCalculatedStats(
        type=PreCalculatedStats.ASSETS_MEDIAN,
        year=2014,
        value=25000.00,
    ).save()
    PreCalculatedStats(
        type=PreCalculatedStats.ASSETS_MEDIAN,
        year=2016,
        value=3088.05,
    ).save()
    PreCalculatedStats(
        type=PreCalculatedStats.ASSETS_MEDIAN,
        year=2018,
        value=2271.98,
    ).save()
    # When
    stats = AssetStats()
    stats()
    # Then
    expected = [
        {"year": 2014, "value": 25000.00},
        {"year": 2016, "value": 3088.05},
        {"year": 2018, "value": 2271.98},
    ]
    response.assert_called_once_with({"mediana_patrimonios": expected})


@pytest.mark.django_db
def test_assets_stats_method_properly_fetches_stats_with_filters(mocker):
    # Given
    response = mocker.patch("perfil.core.views.JsonResponse")
    FIXTURE = [
        Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
        Path() / "perfil" / "core" / "tests" / "fixtures" / "bemdeclarado.csv",
    ]
    call_command("load_candidates", str(FIXTURE[0]))
    call_command("load_assets", str(FIXTURE[1]))
    # When
    stats = AssetStats(states=["DF", "SP"])
    stats()
    # Then
    expected = [
        {"year": 2016, "value": 40900.87},
        {"year": 2018, "value": 80000.00},
    ]
    response.assert_called_once_with({"mediana_patrimonios": expected})


@pytest.mark.django_db
def test_assets_stats_method_returns_empty_list_when_no_values_are_found(mocker):
    # Given
    response = mocker.patch("perfil.core.views.JsonResponse")
    FIXTURE = [
        Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
        Path() / "perfil" / "core" / "tests" / "fixtures" / "bemdeclarado.csv",
    ]
    call_command("load_candidates", str(FIXTURE[0]))
    call_command("load_assets", str(FIXTURE[1]))
    # When
    stats = AssetStats(posts=["deputado distrital", "governador"])
    stats()
    # Then
    expected = [
        {"year": 2016, "value": 40900.87},
        {"year": 2018, "value": 80000.00},
    ]
    response.assert_called_once_with({"mediana_patrimonios": expected})


@pytest.mark.django_db
def test_assets_stats_method_returns_empty_list_when_no_values_are_found(mocker):
    # Given
    response = mocker.patch("perfil.core.views.JsonResponse")
    FIXTURE = [
        Path() / "perfil" / "core" / "tests" / "fixtures" / "candidatura.csv",
        Path() / "perfil" / "core" / "tests" / "fixtures" / "bemdeclarado.csv",
    ]
    call_command("load_candidates", str(FIXTURE[0]))
    call_command("load_assets", str(FIXTURE[1]))
    # When
    stats = AssetStats(states=["MG"], posts=["vereador"])
    stats()
    # Then
    expected = []
    response.assert_called_once_with({"mediana_patrimonios": expected})

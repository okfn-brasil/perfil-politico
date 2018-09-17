import json

import pytest
from django.shortcuts import resolve_url

from perfil.core.models import Candidate


@pytest.mark.django_db
def test_candidate_list(client, candidates):
    candidate = Candidate.objects.filter(year=2018).first()
    candidate.post = "1O SUPLENTE"
    candidate.state = "DF"
    candidate.save()

    url = resolve_url("api_candidate_list", candidate.year, "df", "1o-suplente")
    response = client.get(f"{url}?search=OBA")
    assert 200 == response.status_code

    candidates = json.loads(response.content.decode("utf-8"))
    assert 1 == len(candidates["objects"])
    assert "id" in candidates["objects"][0]
    assert "name" in candidates["objects"][0]
    assert "party" in candidates["objects"][0]
    assert "image" in candidates["objects"][0]
    assert "elections" in candidates["objects"][0]
    assert "elections_won" in candidates["objects"][0]
    assert "gender" in candidates["objects"][0]
    assert "ethnicity" in candidates["objects"][0]


@pytest.mark.django_db
def test_candidate_detail(client, candidates):
    candidate = Candidate.objects.filter(year=2018).first()
    candidate.politician.asset_history = [
        {"year": 2018, "value": 42.0},
        {"year": 2014, "value": 21.0},
    ]
    candidate.politician.affiliation_history = [
        {"party": "PP", "started_in": "2003-10-02"},
        {"party": "AV", "started_in": "1999-09-30"},
    ]
    candidate.politician.election_history = [
        {
            "post": "DEPUTADO DISTRITAL",
            "year": 2018,
            "result": "ELEITO",
            "elected": True,
        },
        {
            "post": "DEPUTADO DISTRITAL",
            "year": 2016,
            "result": "NAO ELEITO",
            "elected": False,
        },
    ]
    candidate.politician.save()

    response = client.get(resolve_url("api_candidate_detail", candidate.pk))
    assert 200 == response.status_code

    content = json.loads(response.content.decode("utf-8"))
    assert content["name"] == candidate.name
    assert content["image"] == candidate.image()
    assert content["ballot_name"] == candidate.ballot_name
    assert content["city"] == candidate.politician.current_affiliation.city.name
    assert content["state"] == candidate.state
    assert content["party"] == candidate.party.name
    assert content["party_abbreviation"] == candidate.party.abbreviation
    assert content["affiliation_history"] == [
        {"party": "AV", "started_in": "1999-09-30"},
        {"party": "PP", "started_in": "2003-10-02"},
    ]
    assert content["asset_history"] == [
        {"year": 2014, "value": 21.0},
        {"year": 2018, "value": 42.0},
    ]
    assert content["election_history"] == [
        {
            "post": "DEPUTADO DISTRITAL",
            "year": 2016,
            "result": "NAO ELEITO",
            "elected": False,
        },
        {
            "post": "DEPUTADO DISTRITAL",
            "year": 2018,
            "result": "ELEITO",
            "elected": True,
        },
    ]
    assert content["elections"] == 2
    assert content["elections_won"] == 1

import json

import pytest
from django.shortcuts import resolve_url

from perfil.core.models import Candidate


@pytest.mark.django_db
def test_candidate_list_with_search(client, candidates):
    candidate = Candidate.objects.filter(year=2018).first()
    candidate.ballot_name = "foobar"
    candidate.save()

    url = resolve_url("api_candidate_list")
    response = client.get(f"{url}?search=OBA")
    assert 200 == response.status_code

    candidates = json.loads(response.content.decode("utf-8"))
    assert 1 == len(candidates["objects"])


@pytest.mark.django_db
def test_candidate_list_without_search(client, candidates):
    response = client.get(resolve_url("api_candidate_list"))
    assert 200 == response.status_code

    candidates = json.loads(response.content.decode("utf-8"))
    assert 0 == len(candidates["objects"])


@pytest.mark.django_db
def test_candidate_detail(client, candidates):
    candidate = Candidate.objects.filter(year=2018).first()
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
    assert content["party_affiliation_history"] == list()

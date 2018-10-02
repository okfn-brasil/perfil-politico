import json
from pathlib import Path

import pytest
from aioresponses import aioresponses
from django.core.management import call_command

from perfil.core.models import Candidate, Politician


FIXTURES = (
    Path() / "perfil" / "core" / "tests" / "fixtures" / "jarbas1.json",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "jarbas2.json",
)

URLS = (
    (
        "https://jarbas.serenata.ai/"
        "api/chamber_of_deputies/reimbursement/"
        "?format=json&limit=7&offset=0&suspicions=1"
    ),
    (
        "https://jarbas.serenata.ai/"
        "api/chamber_of_deputies/reimbursement/"
        "?format=json&limit=7&offset=7&suspicions=1"
    ),
)


def wrap_fixture(json_path):
    with open(json_path) as fobj:
        return json.load(fobj)


@pytest.mark.django_db
def test_suspicions_were_created(candidates, mocker):
    requests = mocker.patch(
        "perfil.core.management.commands.load_rosies_suspicions.requests"
    )
    requests.get.return_value.json.return_value = wrap_fixture(FIXTURES[0])

    names = ("DANIEL COELHO", "CLAUDIO CAJADO", "HERCULANO PASSOS")
    for name, candidate in zip(names, Candidate.objects.all()):
        candidate.name = name
        candidate.ballot_name = name
        candidate.save()

    with aioresponses() as aiohttp_mock:
        for url, fixture in zip(URLS, FIXTURES):
            aiohttp_mock.get(url, payload=wrap_fixture(fixture))
        call_command("load_rosies_suspicions")

    assert 3 == Politician.objects.exclude(rosies_suspicions=[]).count()

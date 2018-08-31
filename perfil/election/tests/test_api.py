import json

import pytest

from perfil.election.tests.factories import ElectionFactory
from perfil.party.tests.factories import PartyFactory
from perfil.person.tests.factories import PersonFactory


@pytest.fixture
def people():
    jon = PersonFactory(civil_name="JOHN SNOW")
    tyrion = PersonFactory(civil_name="TYRION LANNISTER")

    party = PartyFactory()

    # jon elected for president
    ElectionFactory(position="29", result="1", year=1999, party=party, candidate=jon)

    # jon elected by qupta for federal deputy
    ElectionFactory(position="15", result="2", year=1995, party=party, candidate=jon)

    # tyrion not elected for president
    ElectionFactory(position="29", result="4", year=1999, party=party, candidate=tyrion)
    return jon, tyrion


@pytest.mark.django_db
@pytest.mark.parametrize(
    "position,year,qty,expected",
    [
        ("presidente", "year=1999", 2, ["JOHN SNOW", "TYRION LANNISTER"]),
        ("presidente", "", 2, ["JOHN SNOW", "TYRION LANNISTER"]),
        ("deputado+federal", "year=1995", 1, ["JOHN SNOW"]),
        ("deputado+federal", "year=1993", 0, []),
    ],
)
def test_filter_election_by_position(client, people, position, year, qty, expected):
    response = client.get(
        f"/election/position/?position={position}&{year}", follow=True
    )
    content = json.loads(response.content)
    names = [obj["nome"] for obj in content["objects"]]
    assert names == expected
    assert content["per_page"] == 10
    assert content["count"] == qty
    assert content["num_page"] == 1

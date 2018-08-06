import pytest

from perfil.election.tests.factories import ElectionFactory
from perfil.person.tests.factories import PersonFactory
from perfil.party.tests.factories import PartyFactory


@pytest.fixture
def person():
    person = PersonFactory(civil_name='JOHN SNOW')

    party_a = PartyFactory(initials='AA')
    party_b = PartyFactory(initials='BB')

    ElectionFactory(party=party_a, candidate=person)
    ElectionFactory(party=party_b, candidate=person)
    ElectionFactory(party=party_b, candidate=person)
    return person


@pytest.mark.django_db
def test_election_parties(person):
    assert set(person.election_parties) == set(['AA', 'BB'])

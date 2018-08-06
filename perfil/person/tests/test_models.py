import pytest

from perfil.election.tests.factories import AssetFactory, ElectionFactory
from perfil.person.tests.factories import PersonFactory
from perfil.party.tests.factories import PartyFactory


@pytest.fixture
def person():
    person = PersonFactory(civil_name='JOHN SNOW')

    party_a = PartyFactory(initials='AA')
    party_b = PartyFactory(initials='BB')

    election_0 = ElectionFactory(party=party_a, candidate=person, year=2010)
    election_1 = ElectionFactory(party=party_b, candidate=person, year=2014)
    election_2 = ElectionFactory(party=party_b, candidate=person, year=2018)

    AssetFactory(election=election_0, value=10.)
    AssetFactory(election=election_0, value=20.)
    AssetFactory(election=election_1, value=15.)
    AssetFactory(election=election_2, value=34.)

    return person


@pytest.mark.django_db
def test_election_parties(person):
    assert set(person.election_parties) == set(['AA', 'BB'])


@pytest.mark.django_db
def test_asset_evolution(person):
    assets = person.asset_evolution
    assert assets[2010] - 30. < 0.01
    assert assets[2014] - 15. < 0.01
    assert assets[2018] - 34. < 0.01

import factory
from factory.fuzzy import FuzzyInteger, FuzzyFloat

from perfil.election.models import Asset, Election
from perfil.party.tests.factories import PartyFactory
from perfil.person.tests.factories import PersonFactory


class ElectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Election

    candidate = factory.SubFactory(PersonFactory)
    party = factory.SubFactory(PartyFactory)
    year = FuzzyInteger(1996, 2016)


class AssetFactory(factory.DjangoModelFactory):
    class Meta:
        model = Asset

    election = factory.SubFactory(ElectionFactory)
    value = FuzzyFloat(0.5, 10000000)

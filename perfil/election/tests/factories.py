import factory
from factory.fuzzy import FuzzyInteger

from perfil.election.models import Election
from perfil.party.tests.factories import PartyFactory
from perfil.person.tests.factories import PersonFactory


class ElectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Election

    candidate = factory.SubFactory(PersonFactory)
    party = factory.SubFactory(PartyFactory)
    year = FuzzyInteger(1996, 2016)

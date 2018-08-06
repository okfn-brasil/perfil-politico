import factory
from factory.fuzzy import FuzzyChoice

from perfil.party.models import Party


class PartyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Party

    initials = FuzzyChoice(['AA', 'BB', 'CC', 'DD', 'EE', 'FF', 'GG'])

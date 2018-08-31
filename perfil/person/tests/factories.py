import factory
from factory.fuzzy import FuzzyInteger

from perfil.person.models import Person


class PersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = Person

    civil_name = factory.Faker("name")
    cpf = FuzzyInteger(0, 99999999999)

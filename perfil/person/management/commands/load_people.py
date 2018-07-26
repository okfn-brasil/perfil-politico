from perfil.person.models import Person
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    model = Person
    headers = ('cpf', 'civil_name')
    bulk_size = 2 ** 13

from perfil.party.models import Party
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    model = Party
    headers = ('initials', 'name')
    bulk_size = 2 ** 13

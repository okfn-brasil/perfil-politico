from perfil.utils.management.commands import ImportCsvCommand

from perfil.election.management.commands import party_keys, person_keys_birthdate
from perfil.mandate.models import PartyFiliation
from perfil.party.models import Party
from perfil.person.models import Person


class Command(ImportCsvCommand):

    to_cache = ((Person, person_keys_birthdate), (Party, party_keys))
    model = PartyFiliation
    bulk_size = 2 ** 10
    slice_csv = False
    headers = ("name", "birthday", "congressperson_id", "sigla_partido")

    def serialize(self, reader, total, progress_bar):
        for row in reader:
            person_id = self.cache.get(person_keys_birthdate(row))
            party_id = self.cache.get(party_keys(row))
            if person_id and party_id:
                yield PartyFiliation(person_id=person_id, party_id=party_id)
            else:
                yield None

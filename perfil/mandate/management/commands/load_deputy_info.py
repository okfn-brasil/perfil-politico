from unidecode import unidecode


from perfil.election.management.commands import person_keys_birthdate
from perfil.mandate.models import Politician
from perfil.person.models import Person
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    to_cache = ((Person, person_keys_birthdate),)
    model = Politician
    bulk_size = 2 ** 10
    slice_csv = False
    headers = (
        "name",
        "deputy_name",
        "congressperson_id",
        "birthday",
        "birthplace",
        "parents",
        "state",
        "career",
        "link",
        "parties_filiated",
        "term" "congressperson_name",
        "twitter_profile",
        "secondary_twitter_profile",
        "facebook_page",
    )

    def serialize(self, reader, total, progress_bar):
        for row in reader:
            row["name"] = row["name"].replace("  ", " ")
            person_id = self.cache.get(person_keys_birthdate(row))
            if person_id:
                yield Politician(
                    congressperson_id=row["congressperson_id"],
                    congressperson_name=row["deputy_name"],
                    congressperson_bio=row["link"],
                    person_id=person_id,
                    twitter=row["twitter_profile"],
                    second_twitter=row["secondary_twitter_profile"],
                    facebook=row["facebook_page"],
                )
            else:
                yield None

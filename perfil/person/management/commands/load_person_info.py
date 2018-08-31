from textwrap import dedent

from django.core.management.base import BaseCommand

from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.person.models import Person, PersonInformation


class Command(BaseCommand):

    help = dedent(
        """"
        Fill the auxiliary table PersonInformation based on models
        Person, PartyFiliation, Election, Asset
    """
    )
    model = PersonInformation
    bulk_size = 2 ** 10
    slice_csv = False

    def handle(self, *args, **options):
        desc = "Creating Information table"
        people = Person.objects.all()
        total = people.count()

        # choices of Federal Deputy and Senate on Election model
        position_congress = ["15", "16", "17", "18", "25", "26", "27", "28"]

        # choices of Elected and Elected by Party Quota on Election model
        elected_choices = ["1", "2"]

        with tqdm(total=total, desc=desc, unit="people") as progress:
            infos = []
            for person in people:
                election_parties = person.election_parties
                filiation_parties = person.filiation_parties
                parties_change = len(set(filiation_parties + election_parties))

                elections_results = list(
                    person.elections.values_list("result", flat=True)
                )
                num_elections = len(elections_results)
                elected_by_quota = elections_results.count("2")
                elected = elections_results.count("1")
                total_elections_won = elected_by_quota + elected

                congressperson = False
                elections = list(person.elections.values_list("position", "result"))

                # Check if person was elected to federal deputy or senate
                for election in elections:
                    position = election[0]
                    result = election[1]

                    verification = [
                        position in position_congress,
                        result in elected_choices,
                    ]
                    if all(verification):
                        congressperson = True
                        break

                infos.append(
                    PersonInformation(
                        person=person,
                        civil_name=person.civil_name,
                        num_elections=num_elections,
                        total_elections_won=total_elections_won,
                        num_elections_won_by_quota=elected_by_quota,
                        biggest_asset_evolutions=person.biggest_asset_evolution,
                        election_parties=str(election_parties),
                        election_parties_changed=len(election_parties),
                        filiation_parties=set(filiation_parties),
                        filiation_parties_changed=len(filiation_parties),
                        total_parties_changed=parties_change,
                        elected_as_congressperson=congressperson,
                    )
                )

            for bulk in ipartition(infos, self.bulk_size):
                PersonInformation.objects.bulk_create(bulk)
                progress.update(len(bulk))

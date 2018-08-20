from django.core.management.base import BaseCommand

from tqdm import tqdm

from perfil.person.models import Person, PersonInformation


class Command(BaseCommand):

    help = ""
    model = PersonInformation
    bulk_size = 2 ** 10
    slice_csv = False

    def handle(self, *args, **options):
        desc = 'Creating Information table'
        total = Person.objects.count()
        people = Person.objects.all()

        position_congress = ['15', '16', '17', '18', '25', '26', '27', '28']

        with tqdm(total=total, desc=desc, unit='people') as progress:
            infos = []
            count = 0
            for p in people:
                election_parties = p.election_parties
                filiation_parties = p.filiation_parties
                parties_change = len(set(filiation_parties + election_parties))

                elections_results = list(p.elections.values_list('result',
                                                                 flat=True))
                num_elections = len(elections_results)
                elected_by_quota = elections_results.count('2')
                elected = elections_results.count('1')
                total_elections_won = elected_by_quota + elected

                congressperson = False
                elections = list(p.elections.values_list('position', 'result'))
                for election in elections:
                    position = election[0]
                    result = election[1]
                    if position in position_congress and result in ['1', '2']:
                        congressperson = True
                        break

                infos.append(PersonInformation(
                    person=p,
                    civil_name=p.civil_name,
                    num_elections=num_elections,
                    total_elections_won=total_elections_won,
                    num_elections_won_by_quota=elected_by_quota,
                    biggest_asset_evolutions=p.biggest_asset_evolution,
                    election_parties=str(election_parties),
                    election_parties_changed=len(election_parties),
                    filiation_parties=set(filiation_parties),
                    filiation_parties_changed=len(filiation_parties),
                    total_parties_changed=parties_change,
                    elected_as_congressperson=congressperson,
                ))
                count += 1
                if count == self.bulk_size:
                    PersonInformation.objects.bulk_create(infos)
                    infos, count = [], 0
                    progress.update(self.bulk_size)

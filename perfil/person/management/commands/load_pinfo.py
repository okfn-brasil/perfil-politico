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
        people = Person.objects.prefetch_related('elections')\
            .prefech_related('filiations').all()
        with tqdm(total=total, desc=desc, unit='people') as progress:
            for p in people:
                PersonInformation(
                    person=p,
                    num_of_elections=p.elections.count(),
                    num_of_elections_won=p.elections.filter(
                        result__in=['1', '2']).count(),
                    biggest_asset_evolutions=p.biggest_asset_evolution,
                    total_parties_changed=len(set(
                        p.election_parties + p.filiation_parties)),
                    election_parties=str(p.election_parties),
                    filiation_parties=str(p.filiation_parties)
                ).save()
                progress.update(1)

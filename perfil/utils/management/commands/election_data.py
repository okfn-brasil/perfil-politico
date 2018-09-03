import csv

from django.core.management.base import BaseCommand
from django.db.models import Sum
from tqdm import tqdm

from perfil.person.models import Person


class Command(BaseCommand):

    fieldnames = (
        'id',
        'name',
        'voter_id',
        'num_of_elections_run',
        'year',
        'state',
        'party',
        'position',
        'result',
        'sum_of_assets_declared',
        'num_of_assets_declared',
    )

    def _get_total(self):
        for person in Person.objects.filter(elections__year=self.year):
            yield person.elections.count()

    def _election_data(self):
        for person in Person.objects.filter(elections__year=self.year):
            for info in person.elections.all():
                data = (
                    person.id,
                    person.civil_name,
                    person.voter_id,
                    person.elections.count(),
                    info.year,
                    info.state,
                    info.party.initials,
                    info.get_position_display(),
                    info.get_result_display(),
                    info.assets.aggregate(Sum('value'))['value__sum'],
                    info.assets.count()
                )
                yield dict(zip(self.fieldnames, data))

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('output', help='CSV file')

    def handle(self, *args, **options):
        self.year = options.get('year')
        self.output = options.get('output')

        with open(self.output, 'w') as fobj:
            reader = csv.DictWriter(fobj, fieldnames=self.fieldnames)
            reader.writeheader()

            total = sum(self._get_total())
            for data in tqdm(self._election_data(), total=total):
                reader.writerow(data)

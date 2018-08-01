from contextlib import contextmanager
from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from rows.plugins.utils import ipartition


class ImportCsvCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.count = 0
        self.path = None

    def add_arguments(self, parser):
        parser.add_argument('csv', help='Path to CSV file')

    def handle(self, *args, **options):
        self.path = Path(options['csv'])
        if not self.path.exists():
            raise CommandError(f'{self.path} does not exist')

        with open(self.path) as fobj:

            if hasattr(self, 'headers'):
                reader = DictReader(fobj, fieldnames=self.headers)
                next(reader)  # skip header row
            else:
                reader = DictReader(fobj)

            for bulk in ipartition(self.serialize(reader), self.bulk_size):
                self.model.objects.bulk_create(bulk)
                self.stats(len(bulk))

            print(self.message)

    def serialize(self, reader):
        yield from (self.model(**line) for line in reader)

    def stats(self, items_added):
        self.count += items_added
        print(self.message, end='\r')

    @property
    def message(self):
        return f'{self.count:,} {self.model._meta.verbose_name_plural} added'

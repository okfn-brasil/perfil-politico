import csv
from argparse import RawTextHelpFormatter
from contextlib import ContextDecorator
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management.base import BaseCommand, CommandError
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.utils.cache import DiskCache


class CsvSlicer(ContextDecorator):
    """Slice CSV into smaller files. Use it as a context manager."""

    def __init__(self, csv_path, bulk_size, headers=None):
        self.csv_path = csv_path
        self.bulk_size = bulk_size
        self.headers = headers
        self.tmp = TemporaryDirectory()
        self.slices = []

        print("\nReading CSV…")
        with open(csv_path) as input:
            self.total_lines = sum(1 for line in input)

        if not self.headers:
            self.total_lines -= 1

        self.total_slices = ceil(self.total_lines / self.bulk_size)

    @property
    def model_name(self):
        try:
            return self.model._meta.verbose_name
        except AttributeError:
            return self.model.__name__.lower()

    @property
    def readers(self):
        for slice in self.slices:
            with open(slice) as fobj:
                yield csv.DictReader(fobj)

    def __enter__(self):
        with open(self.csv_path) as input:
            reader = csv.reader(input)
            headers = self.headers or next(reader)

            total = self.total_slices
            desc = "Slicing CSV into smaller files"
            with tqdm(total=total, desc=desc, unit="slices") as progress_bar:
                slices = ipartition(reader, self.bulk_size)
                for count, lines in enumerate(slices):
                    output_path = Path(self.tmp.name) / f"{count}.csv"
                    with open(output_path, "w") as output:
                        writer = csv.writer(output)
                        writer.writerow(headers)
                        writer.writerows(lines)

                    self.slices.append(output_path)
                    progress_bar.update(1)

        return self

    def __exit__(self, *args):
        print("\nCleaning up…")
        self.tmp.cleanup()


class ImportCsvCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.count = 0
        self.path = None
        self.cache = None
        self.import_errors = 0

    def create_parser(self, *args, **kwargs):
        """Allow multi-line help text"""
        parser = super(ImportCsvCommand, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("csv", help="Path to CSV file")

    def handle(self, *args, **options):
        with DiskCache() as cache:
            self.cache = cache
            self.path = Path(options["csv"])

            # check if CSV exists
            if not self.path.exists():
                raise CommandError(f"{self.path} does not exist")

            # Pre-cache related models
            for model, get_key in getattr(self, "to_cache", tuple()):
                desc = f"Caching {self.model_name} data"
                total = model.objects.count()
                unit = model._meta.verbose_name_plural
                with tqdm(total=total, desc=desc, unit=unit) as progress_bar:
                    for obj in model.objects.iterator():
                        cache.set(get_key(obj), obj.id)
                        progress_bar.update(1)

            # import
            slice = getattr(self, "slice_csv", True)
            method = self.slice_and_import_csv if slice else self.import_csv
            method()

            if self.import_errors:
                print(f"{self.import_errors:,} lines could not be imported")

    def import_bulk(self, bulk, progress_bar):
        """Generic import method used in `import_csv` and in
        `slice_and_import_csv` methods."""
        bulk = tuple(bulk)
        objects = tuple(obj for obj in bulk if isinstance(obj, self.model))
        self.model.objects.bulk_create(objects)
        progress_bar.update(len(bulk))

        diff = len(bulk) - len(objects)
        if diff:
            self.import_errors += diff

    def import_csv(self):
        headers = getattr(self, "headers", None)
        with open(self.path) as fobj:
            total_lines = sum(1 for line in fobj.readlines())
            fobj.seek(0)

            reader = csv.DictReader(fobj, fieldnames=headers)
            desc = f"Importing {self.model_name} data"
            with tqdm(total=total_lines, desc=desc, unit="lines") as progress:
                objects = self.serialize(reader, total_lines, progress)
                for bulk in ipartition(objects, self.bulk_size):
                    self.import_bulk(bulk, progress)

    def slice_and_import_csv(self):
        kwargs = {
            "bulk_size": self.bulk_size,
            "headers": getattr(self, "headers", None),
        }
        with CsvSlicer(self.path, **kwargs) as source:
            desc = f"Importing {self.model_name} data"
            total = source.total_lines
            with tqdm(total=total, desc=desc, unit="lines") as progress:
                for reader in source.readers:
                    self.import_bulk(self.serialize(reader, total, progress), progress)

    def serialize(self, reader):
        yield from (self.model(**line) for line in reader)

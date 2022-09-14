import csv
import lzma
from argparse import RawTextHelpFormatter
from contextlib import ContextDecorator
from datetime import datetime
from functools import lru_cache
from logging import getLogger
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import base
from django.db.models import Q, Max, Min
from django.utils.timezone import get_default_timezone
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.models import (
    Candidate,
    City,
    Party,
    Politician,
)


def parse_integer(value):
    if not value or not isinstance(value, str):
        return

    try:
        return int(value)
    except ValueError:
        return None


def parse_date(value):
    if not value or not isinstance(value, str):
        return

    patterns_and_lengths = (("%d/%m/%Y", 10), ("%d/%m/%y", 8), ("%Y-%m-%d", 10))
    for pattern, length in patterns_and_lengths:
        cleaned = value[:length]
        try:
            return datetime.strptime(cleaned, pattern).date()
        except (ValueError, TypeError):
            pass

    return None


def parse_datetime(value):
    if not value or not isinstance(value, str):
        return

    patterns = ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S")
    for pattern in patterns:
        try:
            return datetime.strptime(value, pattern).astimezone(get_default_timezone())
        except (ValueError, TypeError):
            pass

    return None


def remove_extra_spaces(value):
    return " ".join(value.split())


@lru_cache(maxsize=1024)
def get_politician(name, post=None):
    name = name.upper()

    def get_match(qs, post=None):
        if post:
            qs = qs.filter(post=post)

        qs = (
            qs.exclude(politician_id=None)
            .values("politician_id")
            .order_by("-politician_id")
            .distinct()
        )
        matches = tuple(qs)

        if len(matches) != 1:  # cannot find a single match
            return None

        match, *_ = matches
        return Politician.objects.get(pk=match["politician_id"])

    qs = Candidate.objects.filter(Q(ballot_name=name) | Q(name=name))
    match = get_match(qs, post=post)

    if not match:
        qs = Candidate.objects.all()
        for word in name.split():
            if len(word) <= 3:
                continue
            qs = qs.filter(Q(ballot_name__contains=word) | Q(name__contains=word))

        match = get_match(qs, post=post)

    return match


@lru_cache(maxsize=1024)
def get_candidate(year, state, sequential):
    kwargs = dict(year=year, state=state, sequential=sequential)
    candidates = tuple(Candidate.objects.filter(**kwargs))

    if len(candidates) == 1:  # yay, there's only match!
        return candidates[0]

    if len(candidates) == 2 and candidates[0].round != candidates[1].round:
        for candidate in candidates:
            if candidate.round == 1:
                return candidate

    return None


@lru_cache(maxsize=1024)
def get_city(name, state):
    city, _ = City.objects.get_or_create(name=name, state=state)
    return city


@lru_cache(maxsize=64)
def get_party(abbreviation, name):
    party, _ = Party.objects.get_or_create(abbreviation=abbreviation, name=name)
    return party


class CsvSlicer(ContextDecorator):
    """Slice CSV into smaller files. Use it as a context manager."""

    def __init__(self, csv_path, bulk_size=2 ** 13, headers=None):
        self.csv_path = csv_path
        self.bulk_size = bulk_size
        self.headers = headers
        self.tmp = TemporaryDirectory()
        self.slices = []

        is_lzma = self.csv_path.name.lower().endswith(".xz")
        self.open = lzma.open if is_lzma else open
        self.extension = ".csv.xz" if is_lzma else ".csv"

        print(f"\nReading {csv_path}…")
        with self.open(csv_path, "rt") as input:
            self.total_lines = sum(1 for line in input)

        if not self.headers:  # one of the lines is the header
            self.total_lines -= 1

        self.total_slices = ceil(self.total_lines / self.bulk_size)

    @property
    def readers(self):
        for slice in self.slices:
            with self.open(slice, "rt") as fobj:
                yield csv.DictReader(fobj)

    def __enter__(self):
        with self.open(self.csv_path, "rt") as input:
            reader = csv.reader(input)
            headers = self.headers or next(reader)

            total = self.total_slices
            desc = f"Slicing {self.csv_path} into smaller files"
            with tqdm(total=total, desc=desc, unit="slices") as progress_bar:
                slices = ipartition(reader, self.bulk_size)
                for count, lines in enumerate(slices):
                    output_path = Path(self.tmp.name) / f"{count}{self.extension}"
                    with self.open(output_path, "wt") as output:
                        writer = csv.writer(output)
                        writer.writerow(headers)
                        writer.writerows(lines)

                    self.slices.append(output_path)
                    progress_bar.update(1)

        return self

    def __exit__(self, *args):
        print("\nCleaning up…")
        self.tmp.cleanup()


class BaseCommand(base.BaseCommand):
    def create_parser(self, *args, **kwargs):
        """Allow multi-line help text"""
        parser = super(BaseCommand, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("csv", help="Path to CSV file")
        parser.add_argument(
            "clean-previous-data",
            default=False,
            nargs="?",
            help=(
                "Creates politicians for all affiliations "
                "regardless if the politician exists or not."
            ),
        )

    def delete_all_objects(self):
        all_objs = self.model.objects.all()
        minor_pk = all_objs.aggregate(Min("pk")).get("pk__min")
        major_pk = all_objs.aggregate(Max("pk")).get("pk__max")

        if not minor_pk or not major_pk:
            print(f"There are no data to delete in {self.model._meta.verbose_name}")
            return

        kwargs = {
            "desc": f"Deleting data from {self.model._meta.verbose_name}...",
            "total": major_pk - minor_pk + 1,
            "unit": "objects",
        }
        offset = minor_pk
        bulk_size = 100
        with tqdm(**kwargs) as progress_bar:
            while offset <= major_pk:
                self.model.objects.filter(
                    pk__gte=offset, pk__lt=offset + bulk_size
                ).delete()
                offset += bulk_size
                progress_bar.update(bulk_size)

    def handle(self, *args, **options):
        self.pre_handle()
        self.log = getLogger(__name__)
        self.path = Path(options["csv"])
        if not self.path.exists():
            raise base.CommandError(f"{self.path} does not exist")

        if options["clean-previous-data"]:
            self.delete_all_objects()

        with CsvSlicer(self.path) as source:
            kwargs = {
                "desc": f"Importing {self.model._meta.verbose_name} data",
                "total": source.total_lines,
                "unit": "lines",
            }
            with tqdm(**kwargs) as progress_bar:
                for reader in source.readers:
                    bulk = tuple(self.serialize(line) for line in reader)
                    objs = (obj for obj in bulk if isinstance(obj, self.model))
                    self.model.objects.bulk_create(objs)
                    progress_bar.update(len(bulk))

        self.post_handle()
        get_city.cache_clear()
        get_candidate.cache_clear()
        get_party.cache_clear()

    def serialize(self, line):
        raise NotImplementedError

    def pre_handle(self):
        pass

    def post_handle(self):
        raise NotImplementedError

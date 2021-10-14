from collections import namedtuple

from django.core.management.base import BaseCommand
from django.db import connection
from django_bulk_update.helper import bulk_update
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.models import Politician, Affiliation


class Command(BaseCommand):
    ignore_existing_politicians = False

    def add_arguments(self, parser):
        parser.add_argument(
            "ignore_existing_politicians",
            default=False,
            nargs="?",
            help=(
                "Creates politicians for all affiliations "
                "regardless if the politician exists or not."
            ),
        )

    def _could_update_politician(self, affiliation: Affiliation) -> bool:
        if self.ignore_existing_politicians:
            return False

        rows = Politician.objects.filter(
            current_affiliation__voter_id=affiliation.voter_id
        ).update(current_affiliation=affiliation)
        return rows > 0

    def _politicians_from_affiliation(self):
        yield from (
            Politician(current_affiliation=affiliation)
            if not self._could_update_politician(affiliation)
            else None
            for affiliation in (
                Affiliation.objects.filter(status="R")
                .order_by("voter_id", "started_in")
                .distinct("voter_id")
                .iterator()
            )
        )

    @staticmethod
    def _affiliations_per_politician():
        Row = namedtuple("Row", ("id", "started_in", "party"))
        print("Worry not: this query takes several minutes to run…")
        sql = """
            SELECT
                politician_voter.politician_id,
                party_voter.started_in,
                party_voter.abbreviation

            FROM (
                SELECT abbreviation, started_in, voter_id
                FROM core_affiliation
                INNER JOIN core_party
                ON core_affiliation.party_id = core_party.id
            ) party_voter

            INNER JOIN (
                SELECT core_politician.id AS politician_id, voter_id
                FROM core_politician
                INNER JOIN core_affiliation
                ON core_politician.current_affiliation_id = core_affiliation.id
            ) politician_voter
            ON politician_voter.voter_id = party_voter.voter_id
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            yield from (Row(*row) for row in cursor.fetchall())

    @staticmethod
    def serialize_bulk(bulk):
        # cache politicians organized by id to quickly retrieve them
        ids = set(row.id for row in bulk)
        politicians = {
            politician.id: politician
            for politician in Politician.objects.filter(id__in=ids)
        }

        # create asset history
        for row in bulk:
            politician = politicians.get(row.id)
            politician.affiliation_history.append(
                {"party": row.party, "started_in": row.started_in.strftime("%Y-%m-%d")}
            )

        yield from politicians.values()

    def handle(self, *args, **options):
        self.ignore_existing_politicians = options["ignore_existing_politicians"]

        # get most recent affiliation to create `Politician` instances
        total = (
            Affiliation.objects.filter(status=Affiliation.REGULAR)
            .values("voter_id")
            .distinct()
            .count()
        )
        kwargs = {
            "desc": f"Importing {Politician._meta.verbose_name} data",
            "total": total,
            "unit": "politicians",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(self._politicians_from_affiliation(), 8192):
                Politician.objects.bulk_create(obj for obj in bulk if obj)
                progress_bar.update(len(bulk))

        # get affiliafill in the `Politician.affiliation_history` field
        assets = tuple(self._affiliations_per_politician())
        kwargs = {
            "desc": f"Creating affiliation history per politician",
            "total": len(assets),
            "unit": "politicians",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(assets, 4096):
                bulk = tuple(self.serialize_bulk(bulk))
                bulk_update(bulk, update_fields=["affiliation_history"])
                progress_bar.update(len(bulk))

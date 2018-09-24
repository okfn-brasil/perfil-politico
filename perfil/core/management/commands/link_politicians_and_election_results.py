from collections import namedtuple

from django.core.management.base import BaseCommand
from django.db import connection
from django_bulk_update.helper import bulk_update
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.models import Politician


class Command(BaseCommand):
    @staticmethod
    def politicians_and_results():
        print("Worry not: this query takes several minutes to run…")
        Row = namedtuple("Row", ("id", "result", "year", "post"))
        sql = """
            SELECT
                affiliation_politician.politician_id,
                core_candidate.round_result,
                core_candidate.year,
                core_candidate.post

            FROM core_candidate

            INNER JOIN (
                SELECT core_politician.id AS politician_id, core_affiliation.voter_id
                FROM core_politician
                INNER JOIN core_affiliation
                ON core_affiliation.id = core_politician.current_affiliation_id
            ) affiliation_politician
            ON affiliation_politician.voter_id = core_candidate.voter_id

            WHERE core_candidate.round_result != ''
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

        # create election history
        for row in bulk:
            politician = politicians.get(row.id)
            politician.election_history.append(
                {
                    "year": int(row.year),
                    "elected": row.result.startswith("ELEIT"),
                    "result": row.result,
                    "post": row.post,
                }
            )

        yield from politicians.values()

    def handle(self, *args, **options):
        results = tuple(self.politicians_and_results())
        kwargs = {"desc": "Election results", "total": len(results), "unit": "results"}
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(results, 4096):
                bulk = tuple(self.serialize_bulk(bulk))
                bulk_update(bulk, update_fields=("election_history",))
                progress_bar.update(len(bulk))

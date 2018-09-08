from django.core.management.base import BaseCommand
from django.db import connection
from django_bulk_update.helper import bulk_update
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.models import Candidate


class Command(BaseCommand):
    @staticmethod
    def candidate_and_politician_pks(year):
        with connection.cursor() as cursor:
            sql = f"""
                SELECT core_candidate.id, politician.id
                FROM core_candidate
                INNER JOIN (
                    SELECT core_politician.id, core_affiliation.voter_id
                    FROM core_politician
                    INNER JOIN core_affiliation
                    ON core_politician.current_affiliation_id = core_affiliation.id
                ) politician
                ON politician.voter_id = core_candidate.voter_id
                WHERE core_candidate.voter_id != '' AND year = {year}
            """
            cursor.execute(sql)
            yield from cursor.fetchall()

    def linked_candidates(self, year):
        links = dict(self.candidate_and_politician_pks(year))
        for candidate in Candidate.objects.filter(pk__in=links.keys()).iterator():
            candidate.politician_id = links[candidate.pk]
            yield candidate

    def link_campaign(self, year):
        kwargs = {
            "desc": str(year),
            "total": Candidate.objects.campaign(year).exclude(voter_id=None).count(),
            "unit": "links",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(self.linked_candidates(year), 4096):
                bulk_update(bulk, update_fields=("politician",))
                progress_bar.update(len(bulk))

    def handle(self, *args, **options):
        years = Candidate.objects.values("year").order_by("-year").distinct()
        for row in years:
            self.link_campaign(row["year"])

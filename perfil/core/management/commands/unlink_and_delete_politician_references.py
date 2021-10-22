from django.db.models import Max, Min
from django.core.management.base import BaseCommand
from django_bulk_update.helper import bulk_update
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.models import Politician, Candidate


class Command(BaseCommand):
    help = "Unlink politician from Candidates so they are not deleted when the politicians data is dropped."

    @staticmethod
    def get_all_candidates_with_politician():
        for candidate in Candidate.objects.filter(politician__isnull=False).iterator():
            yield candidate

    @staticmethod
    def _remove_politician(candidate: Candidate) -> Candidate:
        candidate.politician = None
        return candidate

    def unlink_politicians_and_candidates(self):
        kwargs = {
            "desc": "Unlinking politicians from candidates",
            "total": Candidate.objects.filter(politician__isnull=False).count(),
            "unit": "results",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(self.get_all_candidates_with_politician(), 4096):
                bulk = tuple(self._remove_politician(candidate) for candidate in bulk)
                bulk_update(bulk, update_fields=("politician",))
                progress_bar.update(len(bulk))

    @staticmethod
    def get_max_and_min_politician_pk():
        politicians = Politician.objects.all()
        minor_pk = politicians.aggregate(Min("pk")).get("pk__min")
        major_pk = politicians.aggregate(Max("pk")).get("pk__max")
        return minor_pk, major_pk

    def delete_politicians(self):
        minor_pk, major_pk = self.get_max_and_min_politician_pk()
        if not minor_pk or not major_pk:
            print("There are no politicians on the database to delete")
            return

        kwargs = {
            "desc": "Deleting politicians from database",
            "total": major_pk - minor_pk + 1,
            "unit": "models",
        }
        offset = minor_pk
        bulk_size = 100
        with tqdm(**kwargs) as progress_bar:
            while offset <= major_pk:
                Politician.objects.filter(
                    pk__gte=offset, pk__lt=offset + bulk_size
                ).delete()
                offset += bulk_size
                progress_bar.update(bulk_size)

    def handle(self, *args, **options):
        self.unlink_politicians_and_candidates()
        self.delete_politicians()

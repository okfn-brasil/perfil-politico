from django.core.management.base import BaseCommand
from django_bulk_update.helper import bulk_update
from rows.plugins.utils import ipartition
from tqdm import tqdm

from perfil.core.models import Politician, Candidate


class Command(BaseCommand):
    help = "Unlink politician from Candidates so they are not deleted when the politicians data is dropped."
    model = Politician

    @staticmethod
    def _remove_politician(candidate: Candidate) -> Candidate:
        candidate.politician = None
        return candidate

    def unlink_politicians_and_candidates(self):
        candidates = Candidate.objects.all()
        kwargs = {
            "desc": "Unlinking politicians from candidates",
            "total": len(candidates),
            "unit": "results",
        }
        with tqdm(**kwargs) as progress_bar:
            for bulk in ipartition(candidates, 4096):
                bulk = tuple(self._remove_politician(candidate) for candidate in bulk)
                bulk_update(bulk, update_fields=("politician",))
                progress_bar.update(len(bulk))

    def delete_politicians(self):
        total = self.model.objects.all().count()
        print(f"-> Removing {self.model._meta.verbose_name} data")
        print(f"-> {total} rows found. This may take a while...")
        self.model.objects.all().delete()
        print(f"Done removing {self.model._meta.verbose_name} data.")

    def handle(self, *args, **options):
        self.unlink_politicians_and_candidates()
        self.delete_politicians()

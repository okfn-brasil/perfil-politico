from argparse import RawTextHelpFormatter
from django.core.management import base
from logging import getLogger
from tqdm import tqdm

from perfil.core.models import Affiliation, Candidate, Politician


class Command(base.BaseCommand):
    def create_parser(self, *args, **kwargs):
        """Allow multi-line help text"""
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    help = (
        "Updates affiliation_history for Politicians"
    )
    model = Politician

    def handle(self, *args, **options):
        self.log = getLogger(__name__)

        voter_id_for_politician_id = self.get_distinct_voter_ids_and_politician_ids()
        update_bar_kwargs = {
            "desc": f"Updating {self.model._meta.verbose_name} affiliation history",
            "total": len(voter_id_for_politician_id),
            "unit": "politician",
        }
        with tqdm(**update_bar_kwargs) as progress_bar:
            for voter_id, politician_id in voter_id_for_politician_id:
                self.update_politician(voter_id, politician_id)
                progress_bar.update(1)

    def get_distinct_voter_ids_and_politician_ids(self):
        return (
            Candidate.objects.all()
            .order_by("politician_id")
            .distinct("politician_id")
            .values_list("voter_id", "politician_id")
        )

    def update_politician(self, voter_id, politician_id):
        if not politician_id:
            return

        politician = Politician.objects.get(id=politician_id)
        politician.affiliation_history = self.build_affiliation_history(voter_id)
        politician.save()

    @staticmethod
    def build_affiliation_history(voter_id) -> list:
        affiliations = Affiliation.objects.filter(voter_id=voter_id).values_list(
            "party__abbreviation", "started_in"
        )
        history = []
        for party, started_in in affiliations:
            entry = {"party": party, "started_in": started_in.strftime("%Y-%m-%d")}
            if entry not in history:
                history.append(entry)

        return history

    @staticmethod
    def get_current_affiliation(voter_id) -> Affiliation:
        return Affiliation.objects.filter(
            status=Affiliation.REGULAR,
            voter_id=voter_id,
        ).latest("started_in", "id")


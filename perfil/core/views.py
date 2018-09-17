from django.db import connection
from django.http import Http404, JsonResponse
from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from perfil.core.models import STATES, Candidate


class CandidateListResource(DjangoResource):
    preparer = FieldsPreparer(
        fields={
            "id": "id",
            "name": "ballot_name",
            "party": "party.abbreviation",
            "state": "state",
            "post": "post",
            "image": "image",
            "gender": "gender",
            "ethnicity": "ethnicity",
            "elections": "elections",
            "elections_won": "elections_won",
        }
    )

    def list(self, year, state, post):
        state = state.upper()
        post = post.upper().replace("-", " ")
        return Candidate.objects.campaign(year).filter(post=post, state=state)


class CandidateDetailResource(DjangoResource):
    preparer = FieldsPreparer(
        fields={
            "id": "id",
            "name": "name",
            "image": "image",
            "ballot_name": "ballot_name",
            "city": "politician.current_affiliation.city.name",
            "state": "state",
            "party": "party.name",
            "party_abbreviation": "party.abbreviation",
            "affiliation_history": "affiliation_history",
            "asset_history": "asset_history",
            "elections": "elections",
            "elections_won": "elections_won",
            "election_history": "election_history",
            "date_of_birth": "date_of_birth",
            "city_of_birth": "place_of_birth.name",
            "state_of_birth": "place_of_birth.state",
            "gender": "gender",
            "email": "email",
            "age": "age",
            "ethnicity": "ethnicity",
            "marital_status": "marital_status",
            "education": "education",
            "nationality": "nationality",
            "occupation": "occupation",
            "post": "post",
            "post_code": "post_code",
            "number": "number",
            "coalition_name": "coalition_name",
            "coalition_description": "coalition_description",
            "coalition_short_name": "coalition_short_name",
        }
    )

    def detail(self, pk):
        return Candidate.objects.get(pk=pk)


class Stats:

    STATES = set(abbreviation.lower() for abbreviation, _ in STATES)

    NATIONAL_POSTS = {
        "DEPUTADO DISTRITAL",
        "DEPUTADO ESTADUAL",
        "DEPUTADO FEDERAL",
        "GOVERNADOR",
        "PREFEITO",
        "SENADOR",
        "VEREADOR",
    }

    STATE_POSTS = {
        "DEPUTADO DISTRITAL",
        "DEPUTADO ESTADUAL",
        "DEPUTADO FEDERAL",
        "PREFEITO",
        "SENADOR",
        "VEREADOR",
    }

    CHARACTERICTICS = {
        # TODO "age",
        "education",
        "ethnicity",
        "gender",
        "marital_status",
        "occupation",
        # TODO "party",
        "post",
    }

    def __init__(self, year, post, characteristic, state=None):
        self.state = state.upper() if state else None
        self.year = year
        self.post = post.replace('-', ' ').upper()
        self.characteristic = characteristic.lower()

        self.validate_argument(self.post, self.NATIONAL_POSTS)
        self.validate_argument(self.characteristic, self.CHARACTERICTICS)
        if state:
            self.validate_argument(self.state, self.STATES)

    @staticmethod
    def validate_argument(argument, choices):
        if argument not in choices:
            valid_choices = ', '.join(choices)
            msg = f"{argument} is invalid. Try one of those: {valid_choices}"
            raise Http404(msg)

    @property
    def sql(self):  # TODO use ORM?
        state = f"AND state = '{self.state}'" if self.state else ''
        return f"""
            SELECT {self.characteristic} AS nome, COUNT(id) AS total
            FROM core_candidate
            WHERE year = {self.year}
            AND post = '{self.post}'
            AND round_result LIKE 'ELEIT%'
            {state}
            GROUP BY {self.characteristic}
            ORDER BY total DESC
        """

    def __call__(self):
        with connection.cursor() as cursor:
            cursor.execute(self.sql)
            return JsonResponse([
                {'characteristic': name, 'total': total}
                for name, total in cursor.fetchall()
            ], safe=False)


def national_stats(request, year, post, characteristic):
    stats = Stats(year, post, characteristic)
    return stats()


def state_stats(request, state, year, post, characteristic):
    stats = Stats(year, post, characteristic, state)
    return stats()

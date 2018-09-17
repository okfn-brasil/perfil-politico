from collections import defaultdict

from django.db import connection
from django.http import Http404, JsonResponse
from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from perfil.core.models import STATES, Candidate, age


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
            "age": "get_age",
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
    """Class that supports stats views"""

    STATES = set(abbreviation.upper() for abbreviation, _ in STATES)

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

    CHARACTERISTICS = {
        "age",
        "education",
        "ethnicity",
        "gender",
        "marital_status",
        "occupation",
        "party",
        "post",
    }

    def __init__(self, year, post, characteristic, state=None):
        self.state = state.upper() if state else None
        self.year = year
        self.post = post.replace("-", " ").upper()
        self.characteristic = characteristic.lower()
        self.column = self.get_column_name(self.characteristic)

        self.validate_argument(self.post, self.NATIONAL_POSTS)
        self.validate_argument(self.characteristic, self.CHARACTERISTICS)
        if state:
            self.validate_argument(self.state, self.STATES)

    @staticmethod
    def validate_argument(argument, choices):
        if argument not in choices:
            valid_choices = ", ".join(choices)
            msg = f"{argument} is invalid. Try one of those: {valid_choices}"
            raise Http404(msg)

    @staticmethod
    def get_column_name(characteristic):
        if characteristic == "age":
            return "date_of_birth"
        if characteristic == "party":
            return "core_party.abbreviation"

        return characteristic

    @property
    def sql(self):  # TODO use ORM?
        state, party = "", ""

        if self.state:
            state = f"AND state = '{self.state}'"

        if self.characteristic == "party":
            party = "INNER JOIN core_party ON core_candidate.party_id = core_party.id"

        return f"""
            SELECT {self.column}, COUNT(core_candidate.id) AS total
            FROM core_candidate
            {party}
            WHERE year = {self.year}
              AND post = '{self.post}'
              AND round_result LIKE 'ELEIT%'
              {state}
            GROUP BY {self.column}
            ORDER BY total DESC
        """

    def age_stats(self, data):
        aggregated = defaultdict(int)
        ordered = (
            "less-than-25",
            "between-25-and-34",
            "between-35-and-44",
            "between-45-and-59",
            "between-60-and-69",
            "70-or-more",
        )

        def aggregate(date_of_birth):
            politician_age = age(date_of_birth, self.year)

            if politician_age < 25:
                return "less-than-25"
            if 25 <= politician_age < 35:
                return "between-25-and-34"
            if 35 <= politician_age < 45:
                return "between-35-and-44"
            if 45 <= politician_age < 60:
                return "between-45-and-59"
            if 60 <= politician_age < 70:
                return "between-60-and-69"
            return "70-or-more"

        for row in data:
            date_of_birth, total = row["characteristic"], int(row["total"])
            aggregated[aggregate(date_of_birth)] += total

        return tuple(
            {"characteristic": key, "total": aggregated[key]} for key in ordered
        )

    def __call__(self):
        with connection.cursor() as cursor:
            cursor.execute(self.sql)
            data = tuple(
                {"characteristic": name, "total": total}
                for name, total in cursor.fetchall()
            )

        if self.characteristic == "age":
            data = self.age_stats(data)

        return JsonResponse(data, safe=False)


def national_stats(request, year, post, characteristic):
    stats = Stats(year, post, characteristic)
    return stats()


def state_stats(request, state, year, post, characteristic):
    stats = Stats(year, post, characteristic, state)
    return stats()

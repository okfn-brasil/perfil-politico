from restless.dj import DjangoResource
from restless.exceptions import BadRequest
from restless.preparers import FieldsPreparer

from perfil.core.models import Candidate


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
            # TODO "elections": "elections",
            # TODO "elections_won": "elections_won",
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

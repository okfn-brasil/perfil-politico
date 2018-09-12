from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from perfil.core.models import Candidate


class CandidateResource(DjangoResource):
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
            "ethinicity": "ethinicity",
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

    def list(self):
        query = self.request.GET.get("search", "")
        if not query or len(query) < 3:
            return []

        year = self.request.GET.get("year", 2018)
        return Candidate.objects.campaign(year).filter(ballot_name__icontains=query)

    def detail(self, pk):
        return Candidate.objects.get(pk=pk)

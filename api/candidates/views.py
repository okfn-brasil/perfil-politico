import json

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer
from restless.serializers import JSONSerializer

from models.candidates import Candidates


class CandidateResource(DjangoResource):
    serializer = JSONSerializer()

    def detail(self, pk):
        data = json.loads(Candidates.objects.get(cpf=pk).to_json())
        data.pop('_id')
        return data


class StateResource(DjangoResource):
    serializer = JSONSerializer()

    def detail(self, pk):
        candidates = Candidates.objects.filter(state=pk)
        data = [json.loads(c.to_json()) for c in candidates]
        return data

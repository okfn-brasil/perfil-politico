import json

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer
from restless.serializers import JSONSerializer

from .models import Candidates


class PersonResource(DjangoResource):
    serializer = JSONSerializer()

    def detail(self, pk):
        data = json.loads(Candidates.objects.get(cpf=pk).to_json())
        data.pop('_id')
        return data

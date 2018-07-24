import json

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer
from restless.serializers import JSONSerializer

from .forms import FindByNameForm
from .models import Candidates


class FindByCPFResource(DjangoResource):
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


class FindByNameResource(DjangoResource):
    serializer = JSONSerializer()

    def is_authenticated(self):
        return True

    def create(self):
        form = FindByNameForm(self.data)
        if not form.is_valid():
            raise BadRequest(form.errors)

        name = form.data.get('name').upper()
        persons = Candidates.objects(civil_name__contains=name)
        data = [json.loads(c.to_json()) for c in persons]

        for person in data:
            person.pop('_id')
        return data


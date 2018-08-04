from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from perfil.person.models import Person
from perfil.person.preparers import PERSON_PREPARER


class PersonResource(DjangoResource):

    preparer = FieldsPreparer(fields=PERSON_PREPARER)

    def list(self):
        '''
        The request should be like:  /person/?name=first+last
        '''
        name = self.request.GET.get('name', '').replace('+', ' ')
        return Person.objects.filter(civil_name__contains=name.upper())

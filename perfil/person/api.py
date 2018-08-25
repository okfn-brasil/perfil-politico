from functools import reduce

from django.db.models import Q

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
        name = self.request.GET.get('name', '').upper()
        names = name.split(' ')
        filters = [Q(civil_name__contains=name) for name in names]
        query = reduce(lambda x, y: x & y, filters)
        return Person.objects.filter(query)

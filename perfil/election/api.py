from django.core.paginator import Paginator

from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

from perfil.election.choices import POSITIONS_IDS
from perfil.election.models import Election
from perfil.election.preparers import ELECTION_PREPARER


class ElectionByPositionResource(DjangoResource):

    preparer = FieldsPreparer(fields=ELECTION_PREPARER)

    def list(self):
        '''
        The request should be like:  /person/?position=deputado+estadual&year=2014

        Positions available:
            * vereador
            * prefeito
            * governador
            * deputado+federal
            * deputado+estadual
            * deputado+distrital
            * senador
            * presidente
        '''

        position = self.request.GET.get('position', '')
        positions_ids = POSITIONS_IDS[position.upper()]
        page = self.request.GET.get('page', 1)
        year = self.request.GET.get('year')

        elections = Election.objects.filter(position__in=positions_ids)
        if year:
            elections = elections.filter(year=int(year))

        pagination = Paginator(elections, 10)
        return pagination.page(page).object_list

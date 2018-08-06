from datetime import datetime
from textwrap import dedent

from django.core.cache import cache

from perfil.election.models import Election, Asset
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    help = dedent("""
        Import CSV from https://brasil.io/dataset/eleicoes-brasil/candidatos
    """)

    model = Asset
    bulk_size = 2 ** 13

    @staticmethod
    def election_key(election):
        if isinstance(election, Election):
            keys = (str(election.year), election.state,
                    election.candidate_sequential)
        else:
            keys = (str(election['ano_eleicao']), election['sigla_uf'],
                    election['sq_candidato'])

        key = '-'.join(keys)
        return f'election-{key}'

    def serialize(self, reader):
        print('Caching elections data…')
        for election in Election.objects.all().iterator():
            cache.set(self.election_key(election), election.id, 60 * 60 * 4)

        print('Import asset data…')
        for line in reader:
            election_id = cache.get(self.election_key(line))
            if election_id:
                yield Asset(
                    election_id=election_id,
                    description=line['detalhe_bem'],
                    type=line['cd_tipo_bem_candidato'],
                    value=line['valor_bem']
                )

from textwrap import dedent

from perfil.election.management.commands import election_keys
from perfil.election.models import Election, Asset
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    help = dedent("""
        Import CSV from https://brasil.io/dataset/eleicoes-brasil/candidatos
    """)

    model = Asset
    bulk_size = 2 ** 13
    to_cache = (Election, election_keys),

    def serialize(self, reader):
        for line in reader:
            election_id = self.cache.get(election_keys(line))
            if election_id:
                yield Asset(
                    election_id=election_id,
                    description=line['detalhe_bem'],
                    type=line['cd_tipo_bem_candidato'],
                    value=line['valor_bem']
                )
            else:
                None

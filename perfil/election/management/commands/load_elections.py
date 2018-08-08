from textwrap import dedent

from perfil.election.management.commands import party_keys, person_keys
from perfil.election.models import Election
from perfil.party.models import Party
from perfil.person.models import Person
from perfil.utils.infos import POSITIONS, ELECTION_RESULT
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    help = dedent("""
        Import CSV from https://brasil.io/dataset/eleicoes-brasil/candidatos
    """)

    model = Election
    bulk_size = 2 ** 13
    to_cache = (Person, person_keys), (Party, party_keys)

    def serialize(self, reader):
        for line in reader:
            person_id = self.cache.get(person_keys(line))
            party_id = self.cache.get(party_keys(line))
            if person_id and party_id:
                result = ELECTION_RESULT.get(line['desc_sit_tot_turno'], '0')
                yield Election(
                    candidate_id=person_id,
                    candidate_sequential=line['sequencial_candidato'],
                    legend_composition=line['composicao_legenda'],
                    legend_name=line['nome_legenda'],
                    party_id=party_id,
                    place=line['descricao_ue'],
                    position=POSITIONS[line['descricao_cargo']],
                    result=result,
                    state=line['sigla_uf'],
                    year=line['ano_eleicao'],
                )

from datetime import datetime
from textwrap import dedent

from django.core.cache import cache

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

    @staticmethod
    def person_key(person):
        if isinstance(person, Person):
            keys = person.civil_name, person.cpf
        else:
            keys = person['nome_candidato'], person['cpf_candidato']

        key = '-'.join(keys)
        return f'person-{key}'

    @staticmethod
    def party_key(party):
        if isinstance(party, Party):
            initials = party.initials
        else:
            initials = party['sigla_partido']

        return f'party-{initials}'

    def serialize(self, reader):
        print('Caching person data…')
        for person in Person.objects.all().iterator():
            cache.set(self.person_key(person), person.id, 60 * 60 * 4)

        print('Caching party data…')
        for party in Party.objects.all().iterator():
            cache.set(self.party_key(party), party.id, 60 * 60 * 4)

        print('Import elections data…')
        for line in reader:
            person_id = cache.get(self.person_key(line))
            party_id = cache.get(self.party_key(line))
            if person_id and party_id:
                yield Election(
                    candidate_id=person_id,
                    candidate_sequential=line['sequencial_candidato'],
                    legend_composition=line['composicao_legenda'],
                    legend_name=line['nome_legenda'],
                    party_id=party_id,
                    place=line['descricao_ue'],
                    position=POSITIONS[line['descricao_cargo']],
                    result=ELECTION_RESULT.get(line['desc_sit_tot_turno'], '0'),
                    state=line['sigla_uf'],
                    year=line['ano_eleicao'],
                )

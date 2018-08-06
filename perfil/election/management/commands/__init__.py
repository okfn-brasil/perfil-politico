from perfil.election.models import Election
from perfil.party.models import Party
from perfil.person.models import Person


def election_keys(election):
    if isinstance(election, Election):
        return election.year, election.state, election.candidate_sequential
    return election['ano'], election['uf'], election['numero']


def person_keys(person):
    if isinstance(person, Person):
        return person.civil_name, person.cpf
    return person['nome_candidato'], person['cpf_candidato']


def party_keys(party):
    if isinstance(party, Party):
        return party.initials,
    return party['sigla_partido'],

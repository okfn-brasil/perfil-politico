import json

import pytest

from candidates.models import Candidates


@pytest.fixture
def candidate():
    candidate = Candidates(
        civil_name='John Snow',
        cpf='1234567',
        voter_id='987654',
        state='SP',

    )
    Candidates.objects.insert(candidate)
    return candidate


def test_get_candidate_by_cpf(client, candidate):
    cpf = candidate.cpf
    response = client.get('/candidate/{}'.format(cpf), follow=True)
    assert candidate.to_json() == response.content.decode()


def test_get_candidate_by_state(client, candidate):
    state = candidate.state
    response = client.get('/state/{}'.format(state), follow=True)

    expected = json.loads(candidate.to_json())
    actual = json.loads(response.content)[0]
    actual.pop('_id')
    assert expected == actual

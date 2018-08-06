import json

import pytest

from perfil.person.tests.factories import PersonFactory

@pytest.fixture
def person():
    return [
        PersonFactory(civil_name='JOHN SNOW TARGARYEN'),
        PersonFactory(civil_name='RAMSAY SNOW'),
    ]


@pytest.mark.django_db
@pytest.mark.parametrize('url,qty,expected', [
    ('snow', 2, ['JOHN SNOW TARGARYEN', 'RAMSAY SNOW']),
    ('snow+targaryen', 1, ['JOHN SNOW TARGARYEN']),
    ('snail', 0, []),
])
def test_person_list_by_last_name(client, person, url, qty, expected):
    response = client.get(f'/person/?name={url}', follow=True)
    content = json.loads(response.content)
    names = [obj['nome'] for obj in content['objects']]

    assert len(content['objects']) == qty
    assert names == expected

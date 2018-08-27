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
    ('john+targaryen', 1, ['JOHN SNOW TARGARYEN']),
    ('snail', 0, []),
])
def test_person_list_by_last_name(client, person, url, qty, expected):
    response = client.get(f'/person/?name={url}', follow=True)
    content = json.loads(response.content)
    names = [obj['nome'] for obj in content['objects']]

    assert names == expected
    assert content['per_page'] == 10
    assert content['count'] == qty
    assert content['num_page'] == 1


@pytest.mark.django_db
@pytest.mark.parametrize('query,page', [
    ('', 1),
    ('&page=1', 1),
    ('&page=8', 8),
    ('&page=10', 10),
])
def test_pagination(client, query, page):
    for i in range(100):
        PersonFactory(civil_name='TARGARYEN')

    response = client.get(f'/person/?name=targaryen{query}', follow=True)
    content = json.loads(response.content)

    assert content['per_page'] == 10
    assert content['count'] == 100
    assert content['num_page'] == 10
    assert content['page'] == page

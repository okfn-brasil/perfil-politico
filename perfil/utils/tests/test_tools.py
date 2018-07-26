from datetime import date

import pytest

from perfil.utils.tools import normalize, parse_birthdate, probably_same_entity


@pytest.mark.parametrize('input,expected', [
    ('1/1/1979', date(1979, 1, 1)),
    ('1/1/79', date(1979, 1, 1)),
    (None, None),
    ('', None),
    ('1/1', None),
])
def test_parse_birthdate(input, expected):
    assert parse_birthdate(input) == expected


def test_normalize():
    assert 'aeiouc' == normalize('àéîõùç')


@pytest.mark.parametrize('input,expected', [
    (('Cuducos', 'cuducos', 'Çuducos', 'Cuduco'), True),
    (('Rafael da Silva', 'Raphael de Silva'), True),
    (('Rafael Gomes', 'Raphaello Gomez'), False)
])
def test_probably_same_entity(input, expected):
    assert probably_same_entity(input) == expected

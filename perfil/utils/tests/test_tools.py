from datetime import date
from decimal import Decimal

import pytest

from perfil.utils.tools import (
    parse_date,
    parse_decimal,
    parse_document,
    probably_same_entity
)


@pytest.mark.parametrize('input, expected', [
    ('1/1/1979', date(1979, 1, 1)),
    ('1/1/79', date(1979, 1, 1)),
    (None, None),
    ('', None),
    ('1/1', None)
])
def test_parse_date(input, expected):
    assert parse_date(input) == expected


@pytest.mark.parametrize('input, expected', [
    ('342.663.749-92', '34266374992'),
    ('34266374992', '34266374992'),
    ('000.000.000-00', None),
    ('51.771.685/0001-00', '51771685000100'),
    ('51771685000100', '51771685000100'),
    ('00.000.000/0000-00', None),
    (None, None),
    ('42', None),
    ('1/1', None)
])
def test_parse_document(input, expected):
    assert parse_document(input) == expected


@pytest.mark.parametrize('input, expected', [
    ('3.1415', Decimal('3.1415')),
    ('abc', None),
    (None, None)
])
def test_parse_decimal(input, expected):
    assert parse_decimal(input) == expected


@pytest.mark.parametrize('input,expected', [
    (('Cuducos', 'cuducos', 'Çuducos', 'Cuduco'), True),
    (('Rafael da Silva', 'Raphael de Silva'), True),
    (('Rafael Gomes', 'Raphaello Gomez'), False)
])
def test_probably_same_entity(input, expected):
    assert probably_same_entity(input) == expected

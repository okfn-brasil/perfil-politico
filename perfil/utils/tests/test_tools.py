from datetime import date

import pytest

from perfil.utils.tools import parse_birthdate


@pytest.mark.parametrize('input,expected', [
    ('1/1/1979', date(1979, 1, 1)),
    ('1/1/79', date(1979, 1, 1)),
    (None, None),
    ('', None),
    ('1/1', None),
])
def test_parse_birthdate(input, expected):
    assert parse_birthdate(input) == expected

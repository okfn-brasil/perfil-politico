from datetime import date, datetime

import pytest
from django.core.management.base import CommandError
from django.utils.timezone import utc

from perfil.core.management.commands import (
    BaseCommand,
    parse_integer,
    parse_date,
    parse_datetime,
)


def test_parse_integer():
    assert 42 == parse_integer("42")
    assert parse_integer("3.1415") is None
    assert parse_integer("foobar") is None
    assert parse_integer(None) is None


def test_parse_date():
    assert date(1970, 12, 31) == parse_date("31/12/1970 and whatever")
    assert date(1970, 12, 31) == parse_date("31/12/70 and whatever")
    assert date(1970, 12, 31) == parse_date("1970-12-31 and whatever")
    assert parse_date("") is None
    assert parse_date("not a date") is None


def test_parse_datetime():
    expected = datetime(1970, 12, 31, 1, 2, 3).astimezone(utc)
    assert expected == parse_datetime("31/12/1970 01:02:03").astimezone(utc)
    assert expected == parse_datetime("1970-12-31 01:02:03").astimezone(utc)
    assert parse_datetime("") is None
    assert parse_datetime("not a datetime") is None


def test_command_raises_error_if_csv_path_does_not_exist():
    command = BaseCommand()
    with pytest.raises(CommandError):
        command.handle(csv="not-a-file")


def test_command_raises_error_for_method_not_implemented_yet():
    command = BaseCommand()

    with pytest.raises(NotImplementedError):
        command.serialize(None)

    with pytest.raises(NotImplementedError):
        command.post_handle()

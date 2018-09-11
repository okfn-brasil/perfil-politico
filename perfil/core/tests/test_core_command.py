from datetime import date, datetime

import pytest
from django.core.management.base import CommandError
from django.utils.timezone import utc
from mixer.backend.django import mixer

from perfil.core.management.commands import (
    BaseCommand,
    get_candidate,
    parse_integer,
    parse_date,
    parse_datetime,
)
from perfil.core.models import Candidate


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


@pytest.mark.django_db
def test_get_candidate():
    mixer.blend("core.city", name="Monty Python")
    mixer.blend("core.party")
    mixer.blend("core.affiliation", party=mixer.SELECT, city=mixer.SELECT)
    mixer.cycle(2).blend(
        "core.candidate",
        politician=mixer.blend("core.politician", current_affiliation=mixer.SELECT),
        year=2018,
        sequential="70000601690",
        state="DF",
        round=(round for round in range(1, 3)),
    )
    assert Candidate.objects.get(round=1) == get_candidate(2018, "DF", "70000601690")

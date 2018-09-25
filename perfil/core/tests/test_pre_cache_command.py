from pathlib import Path

import pytest
from django.core.management import call_command

from perfil.core.management.commands.pre_cache import Command, distinct


FIXTURES = (
    Path() / "perfil" / "core" / "tests" / "fixtures" / "affiliation.csv",
    Path() / "perfil" / "core" / "tests" / "fixtures" / "candidate.csv.xz",
)


@pytest.mark.django_db
def test_distinct():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    assert (2018,) == distinct("year", reversed=True)


def test_default_domain(settings):
    settings.ALLOWED_HOSTS = (42, 21)
    command = Command()
    assert 42 == command.default_domain


@pytest.mark.django_db
def test_candidate_list_paths():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    command = Command()
    command.year, command.stats_year = 2018, 2014
    assert len(tuple(command.candidate_list_paths)) == 2


@pytest.mark.django_db
def test_national_stats_paths():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    command = Command()
    command.year, command.stats_year = 2018, 2014
    assert len(tuple(command.national_stats_paths)) == 56


@pytest.mark.django_db
def test_state_stats_paths():
    call_command("load_affiliations", str(FIXTURES[0]))
    call_command("load_candidates", str(FIXTURES[1]))
    command = Command()
    command.year, command.stats_year = 2018, 2014
    assert len(tuple(command.state_stats_paths)) == 56


def test_handle(settings, mocker):
    urlopen = mocker.patch("perfil.core.management.commands.pre_cache.urlopen")
    call_command("pre_cache", 2018, domain="perfilpolitico.serenata.ai", https=True)
    urlopen.assert_any_call(
        "https://perfilpolitico.serenata.ai/api/candidate/2018/df/deputado-distrital/"
    )
    urlopen.assert_any_call(
        "https://perfilpolitico.serenata.ai/api/candidate/2018/df/deputado-federal/"
    )
    assert urlopen.call_count == 114

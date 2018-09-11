from django.shortcuts import resolve_url


def test_status(client, settings):
    settings.DEBUG = True  # disable WhiteNoise
    assert 200 == client.get(resolve_url("home")).status_code

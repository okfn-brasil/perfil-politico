from django.shortcuts import resolve_url


def test_home_redirects_to_frontend(client):
    response = client.get(resolve_url("home"))
    assert 302 == response.status_code
    assert "https://perfilpolitico.serenata.ai/" == response.url

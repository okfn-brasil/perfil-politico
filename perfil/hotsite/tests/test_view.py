def test_status(client, settings):
    settings.DEBUG = True  # disable WhiteNoise
    assert 200 == client.get("/").status_code

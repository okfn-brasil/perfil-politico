import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
def test_candidate_repr():
    city = mixer.blend("core.city", name="Surreal Comedy", state="SC")
    assert "Surreal Comedy - SC" == repr(city)

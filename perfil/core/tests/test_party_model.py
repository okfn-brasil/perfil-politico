import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
def test_candidate_repr():
    party = mixer.blend("core.party", name="Surreal Comedy", abbreviation="SC")
    assert "SC" == repr(party)

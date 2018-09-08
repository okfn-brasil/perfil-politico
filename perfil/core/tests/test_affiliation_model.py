import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
def test_affiliation_repr():
    affiliation = mixer.blend("core.affiliation")
    assert affiliation.name in repr(affiliation)
    assert affiliation.city.state in repr(affiliation)
    assert affiliation.party.abbreviation in repr(affiliation)

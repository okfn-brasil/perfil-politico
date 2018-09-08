import pytest

from perfil.core.models import Politician


@pytest.mark.django_db
def test_politician_repr(candidates):
    politician = Politician.objects.first()
    assert politician.current_affiliation.name in repr(politician)
    assert politician.current_affiliation.city.state in repr(politician)
    assert politician.current_affiliation.party.abbreviation in repr(politician)

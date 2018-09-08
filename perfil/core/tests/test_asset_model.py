import pytest
from mixer.backend.django import mixer


@pytest.mark.django_db
def test_asset_repr(candidates):
    asset = mixer.blend(
        "core.asset", category="FOOBAR", value="1234.56", candidate=mixer.SELECT
    )
    assert "FOOBAR (R$ 1,234.56)" == repr(asset)

import pytest

from perfil.core.models import Bill


@pytest.mark.django_db
def test_bill_repr():
    bill = Bill.objects.create(
        summary="foobar",
        name="FB",
        keywords=("42",),
        source_id=42,
        url="https://example.com",
    )
    assert "FB" == repr(bill)

import pytest
from mixer.backend.django import mixer


@pytest.fixture
def candidates(db):
    mixer.blend("core.city", name="Monty Python")
    mixer.blend("core.party")
    affiliations = mixer.cycle(3).blend(
        "core.affiliation", party=mixer.SELECT, city=mixer.SELECT
    )
    politicians = mixer.cycle(3).blend(
        "core.politician", current_affiliation=(a for a in affiliations)
    )
    mixer.cycle(3).blend(
        "core.candidate",
        politician=(politician for politician in politicians),
        year=(year for year in (2018, 2018, 2016)),
        sequential=(n for n in ("70000601690", "70000625538", "42")),
        ballot_name=(n for n in ("GRAHAM", "JOHN", "TERRY")),
        state="DF",
    )

from mongoengine import (
    BooleanField,
    EmbeddedDocument,
    IntField,
    StringField,
)


class Election(EmbeddedDocument):
    year = IntField()
    party = StringField()
    elected = BooleanField()
    position = StringField()


class ElectionsCount(EmbeddedDocument):
    elections_alternate = IntField()
    elections_elected = IntField()
    elections_elected_by_party_quota = IntField()
    elections_not_elected = IntField()
    elections_rejected = IntField()
    elections_replaced = IntField()
    elections_runoff = IntField()
    times_elected_to_city_councilman = IntField()
    times_elected_to_district_deputy = IntField()
    times_elected_to_federal_deputy = IntField()
    times_elected_to_governor = IntField()
    times_elected_to_mayor = IntField()
    times_elected_to_president = IntField()
    times_elected_to_senate_first_alternate = IntField()
    times_elected_to_senate_second_alternate = IntField()
    times_elected_to_senator = IntField()
    times_elected_to_state_deputy = IntField()
    times_elected_to_vice_governor = IntField()
    times_elected_to_vice_mayor = IntField()
    times_elected_to_vice_president = IntField()

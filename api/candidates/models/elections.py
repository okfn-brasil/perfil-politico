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
    elections_alternate = StringField()
    elections_elected = StringField()
    elections_elected_by_party_quota = StringField()
    elections_not_elected = StringField()
    elections_rejected = StringField()
    elections_replaced = StringField()
    elections_runoff = StringField()
    times_elected_to_city_councilman = StringField()
    times_elected_to_district_deputy = StringField()
    times_elected_to_federal_deputy = StringField()
    times_elected_to_governor = StringField()
    times_elected_to_mayor = StringField()
    times_elected_to_president = StringField()
    times_elected_to_senate_first_alternate = StringField()
    times_elected_to_senate_second_alternate = StringField()
    times_elected_to_senator = StringField()
    times_elected_to_state_deputy = StringField()
    times_elected_to_vice_governor = StringField()
    times_elected_to_vice_mayor = StringField()
    times_elected_to_vice_president = StringField()

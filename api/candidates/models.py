from mongoengine import (
    Document,
    DynamicDocument,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    FloatField,
    IntField,
    StringField,
)


class SessionsByYear(EmbeddedDocument):
    total_sessions = IntField()
    present = IntField()
    abstent = IntField()
    abstent_with_justification = IntField()
    present_percent = FloatField()
    abstent_percent = FloatField()
    abstent_with_justification_percent = FloatField()


class Sessions(EmbeddedDocument):
    year_2015 = EmbeddedDocumentField(SessionsByYear)
    year_2016 = EmbeddedDocumentField(SessionsByYear)
    year_2017 = EmbeddedDocumentField(SessionsByYear)
    year_2018 = EmbeddedDocumentField(SessionsByYear)


class Term(EmbeddedDocument):
    begin = IntField()
    end = IntField()
    congressperson_document = StringField()


class DeputyInfo(EmbeddedDocument):
    congressperson_id = StringField()
    congressperson_name = StringField()
    terms = EmbeddedDocumentListField(Term)


class Elections(EmbeddedDocument):
    elections_alternate = StringField()
    elections_elected  = StringField()
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


class Candidates(Document):
    civil_name = StringField(required=True)
    cpf = StringField(required=True)
    voter_id = StringField()
    state = StringField()
    gender = StringField()
    elections = EmbeddedDocumentField(Elections)
    deputy_info = EmbeddedDocumentField(DeputyInfo)
    sessions_presence = EmbeddedDocumentField(Sessions)

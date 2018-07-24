from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    IntField,
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

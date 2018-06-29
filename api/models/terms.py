from mongoengine import (
    EmbeddedDocument,
    IntField,
    StringField,
)


class Term(EmbeddedDocument):
    begin = IntField()
    end = IntField()
    position = StringField()
    region = StringField()
    party = StringField()
    position_document = StringField()

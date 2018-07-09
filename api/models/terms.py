from mongoengine import (
    EmbeddedDocument,
    IntField,
    StringField,
)


class Term(EmbeddedDocument):
    begin = IntField(null=True)
    end = IntField(null=True)
    position = StringField()
    region = StringField()
    party = StringField()
    position_document = StringField()

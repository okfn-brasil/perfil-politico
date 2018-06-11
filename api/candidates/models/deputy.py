from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentListField,
    IntField,
    StringField,
)


class Term(EmbeddedDocument):
    begin = IntField()
    end = IntField()
    congressperson_document = StringField()


class DeputyInfo(EmbeddedDocument):
    congressperson_id = StringField()
    congressperson_name = StringField()
    terms = EmbeddedDocumentListField(Term)

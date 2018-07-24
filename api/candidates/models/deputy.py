from mongoengine import (
    EmbeddedDocument,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    URLField,
)


class Document(EmbeddedDocument):
    begin = IntField()
    end = IntField()
    congressperson_document = StringField()


class DeputyInfo(EmbeddedDocument):
    congressperson_id = StringField(unique=True, sparse=True)
    congressperson_name = StringField()
    congressperson_bio = URLField()
    documents = EmbeddedDocumentListField(Document)

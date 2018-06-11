from mongoengine import (
    Document,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    StringField,
)

from .deputy import DeputyInfo
from .elections import Election, ElectionsCount
from .sessions import Sessions


class Candidates(Document):
    civil_name = StringField(required=True)
    cpf = StringField(required=True)
    voter_id = StringField()
    state = StringField()
    gender = StringField()
    birthday = StringField()
    elections_count = EmbeddedDocumentField(ElectionsCount)
    deputy_info = EmbeddedDocumentField(DeputyInfo)
    sessions_presence = EmbeddedDocumentField(Sessions)
    elections = EmbeddedDocumentListField(Election)

from mongoengine import (
    Document,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    ListField,
    StringField,
)

from .companies import Company
from .deputy import DeputyInfo
from .elections import Election, ElectionsCount
from .sessions import Sessions


class Candidates(Document):
    civil_name = StringField(required=True)
    cpf = StringField(unique=True, sparse=True)
    voter_id = StringField()
    state = StringField()
    gender = StringField()
    birthday = StringField()
    phone_number = StringField()
    email = StringField()
    picture_url = StringField()
    parties = ListField()
    elections_count = EmbeddedDocumentField(ElectionsCount)
    deputy_info = EmbeddedDocumentField(DeputyInfo)
    sessions_presence = EmbeddedDocumentField(Sessions)
    elections = EmbeddedDocumentListField(Election)
    companies = EmbeddedDocumentListField(Company)

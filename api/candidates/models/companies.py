from mongoengine import (
    BooleanField,
    EmbeddedDocument,
    StringField,
)


class Company(EmbeddedDocument):
    cnpj = StringField()
    company_name = StringField()
    company_state = StringField()
    role = StringField()
    possible_homonym = BooleanField()

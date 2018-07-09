from decouple import config
from mongoengine import connect


def connect_db(local=False):
    if not local:
        connect(host=config('MONGO_URL'))
    else:
        connect('serenata')

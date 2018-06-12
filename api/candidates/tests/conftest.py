from django.test import Client

import mongoengine as me


def pytest_configure():
    me.connection.disconnect()
    me.connect('mongoenginetest', host='mongomock://localhost')


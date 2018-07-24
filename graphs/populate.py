import sys
sys.path.append('/Users/leportella/src/serenata/medidor-de-poder/')

from decouple import config
from mongoengine import connect
from py2neo import Graph, Node, Relationship

from api.candidates.models import Candidates


c = 0
persons = Candidates.objects(elections__exists=True)
for person in persons:
    tx = graph.begin()
    person_node = add_person_node(person)
    add_elections_relationship(person, person_node)
    c += 1
    tx.commit()
    if c > 10:
        break

print('Done :)')

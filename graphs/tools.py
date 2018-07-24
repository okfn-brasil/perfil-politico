from decouple import config
from mongoengine import connect
from py2neo import Graph, Node, Relationship


def get_connection():
    connect(host=config('MONGO_URL'))
    return Graph(auth=(config('NEO4J_USER'), config('NEO4J_PASSWORD')))


def add_person_node(person):
    person_node = Node("Person", name=person.civil_name, cpf=person.cpf)
    tx.merge(person_node, "Person", "cpf")
    print("person created")
    return person_node


def add_elections_relationship(person, person_node):
    parties = list(set([p.party  for p in person.elections]))
    for party in parties:
        party_node = Node("Party", initials=party)
        tx.merge(party_node, "Party", "initials")
        print("party {} created".format(party))

        r = Relationship(person_node, "COMPETED_FOR", party_node)
        tx.merge(r)
        print("relationshop {} created".format(r))

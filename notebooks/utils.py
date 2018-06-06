from collections import Counter

from pymongo import MongoClient

client = MongoClient()


def get_collection():
    db = client.serenata
    return db.candidates


def insert_person_information(cpf, data):
    '''
    Insert an information about a person based on its
    cpf. If the data already exists, it will add the
    data to the old register. If the person is not in the
    database, it is added.

    inser_person_information(cpf, data)

    cpf --> a string with no ponctuation
    data --> a dictionary with information

    return will be one of two strings: 'created' or 'updated'
    '''
    collection = get_collection()
    person = collection.find_one({'cpf': cpf})

    if person:
        person.update(data)
        collection.find_one_and_replace({'cpf': cpf}, person)
        return 'updated'

    collection.insert_one(data)
    return 'created'


def insert_df_to_db(df, object_name=None):
    '''
    inserts the information contained on a dataframe
    to the database. The dataframe must contain a cpf
    field that should not have any ponctuarion.

    insert_df_to_db(df)

    return should be a dictionary:
    {'created': 10, 'updated': 10}
    '''
    status = Counter()
    df.fillna(0, inplace=True)

    for i, row in df.iterrows():
        obj = row.to_dict()
        clean_obj = {key: obj.get(key) for key in obj if obj.get(key)}
        cpf = clean_obj.get('cpf')

        if object_name:
            clean_obj.pop('cpf')
            data = {'cpf': cpf, object_name: clean_obj}
        else:
            data = clean_obj

        answer = insert_person_information(cpf, data)
        status.update((answer,))

    return {'created': status['created'],
            'updated': status['updated']}

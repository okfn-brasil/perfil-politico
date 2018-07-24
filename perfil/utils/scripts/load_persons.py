import sys
import os
import django
from time import sleep

from django.conf import settings

sys.path.append('/code')
os.environ['DJANGO_SETTINGS_MODULE'] = 'perfil.settings'
django.setup()

import pandas as pd

from person.models import Person

df = pd.read_csv('data/cpfs.csv', dtype={'cpf_candidato': str})
print('Dataset loaded...')


persons = []
for i, row in df.iterrows():
    persons.append(Person(civil_name=row['nome_candidato'],
                          cpf=row['cpf_candidato']))
print('List of persons created')

for i in range(0, len(persons)+1, 100):
    if len(persons) > i+100:
        Person.objects.bulk_create(persons[i:i+100])
    else:
        Person.objects.bulk_create(persons[i:])
print('inserted on the db!')

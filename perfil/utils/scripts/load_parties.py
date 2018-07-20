import sys
import os
import django
from time import sleep

sys.path.append('/Users/leportella/src/serenata/new_perfil/perfil/perfil')
os.environ['DJANGO_SETTINGS_MODULE'] = 'perfil.settings'
django.setup()

import pandas as pd

from party.models import Party

df = pd.read_csv('data/parties.csv')

for i, row in df.iterrows():
    Party.objects.get_or_create(initials=row['sigla_partido'],
                                name=row['nome_partido'])
    print('{}/{}'.format(i, df.shape[0]-1), flush=True)

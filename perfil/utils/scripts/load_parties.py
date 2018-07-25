import sys
import os
from pathlib import Path

import django

import pandas as pd

sys.path.append(str(Path().parent.parent))
os.environ['DJANGO_SETTINGS_MODULE'] = 'perfil.settings'
django.setup()

from perfil.party.models import Party  # noqa

df = pd.read_csv('data/parties.csv')

for i, row in df.iterrows():
    Party.objects.get_or_create(initials=row['sigla_partido'],
                                name=row['nome_partido'])
    print('{}/{}'.format(i, df.shape[0]-1), flush=True)

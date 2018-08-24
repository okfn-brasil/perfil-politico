from django.db.models import Sum

from perfil.person.models import Person


labels = [
    'name',
    'num_of_elections_run',
    'year',
    'state',
    'party',
    'position',
    'result',
    'sum_of_assets_declared',
    'num_of_assets_declared',
]
infos = []

for person in Person.objects.filter(elections__year=2018):
    for info in person.elections.all():
        infos.append([
            person.id,
            person.civil_name,
            person.elections.count(),
            info.year,
            info.state,
            info.party.initials,
            info.get_position_display(),
            info.get_result_display(),
            info.assets.aggregate(Sum('value'))['value__sum'],
            info.assets.count()
        ])

thefile = open('asset_evolution_elections_2018.csv', 'w')

for label in labels:
    thefile.write('{},'.format(label))
thefile.write('\n')

for items in infos:
    for item in items:
        thefile.write('{},'.format(item))
    thefile.write('\n')

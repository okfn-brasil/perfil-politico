from perfil.mandate.models import Politician


labels = [
    'name',
    'num_tweets',
    'num_law_projects',
    'top_keywords_bills',
    'top_keywords_tweets',
]

infos = []
for politician in Politician.objects.all():
    bills = politician.count_bills_keywords()
    tweets = politician.count_twitter_keywords()

    infos.append([
        politician.person.civil_name,
        politician.tweets.count(),
        politician.bill_set.count(),
        str(bills.most_common(30)),
        str(tweets.most_common(30)),
    ])



thefile = open('keywords_results.csv', 'w')

for label in labels:
    thefile.write('{};'.format(label))
thefile.write('\n')

for items in infos:
    for item in items:
        thefile.write('{};'.format(item))
    thefile.write('\n')

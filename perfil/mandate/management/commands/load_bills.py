import csv
from unidecode import unidecode

from tqdm import tqdm

from perfil.mandate.models import Bill, Politician
from perfil.utils.tools import parse_date, clean_keywords
from perfil.utils.management.commands import ImportCsvCommand


class Command(ImportCsvCommand):

    model = Bill
    bulk_size = 2 ** 10
    slice_csv = False
    headers = (
        'apresentacao',
        'autoria',
        'ementa',
        'id_site',
        'local',
        'nome',
        'origem',
        'palavras_chave',
        'palavras_chave_originais',
        'url',
    )

    def import_csv(self):
        headers = getattr(self, 'headers', None)
        with open(self.path) as fobj:
            total_lines = sum(1 for line in fobj.readlines())
            fobj.seek(0)

            reader = csv.DictReader(fobj, fieldnames=headers)
            desc = f'Importing {self.model_name} data'
            with tqdm(total=total_lines, desc=desc, unit='lines') as progress:
                for row in reader:
                    if row['autoria'] == 'autoria':
                        continue

                    keywords = clean_keywords(row['palavras_chave'])
                    original_keywords = clean_keywords(
                        row['palavras_chave_originais']
                    )

                    project = Bill(
                        date=parse_date(row['apresentacao']),
                        text=row['ementa'],
                        url_id=row['id_site'],
                        area=row['local'],
                        name=row['nome'],
                        keywords=keywords,
                        original_keywords=original_keywords,
                        url=row['url'],
                    )
                    project.save()

                    authors = row['autoria'].upper().split(',')

                    for author in authors:
                        try:
                            politician = Politician.objects.get(
                                congressperson_name=unidecode(author)
                            )
                            project.authors.add(politician)
                        except Exception as e:
                            pass

                    progress.update(1)

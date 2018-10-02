from collections import Counter

from django_bulk_update.helper import bulk_update
from tqdm import tqdm

from perfil.core.management.commands import BaseCommand, get_politician
from perfil.core.models import Bill, Politician


class Command(BaseCommand):
    help = (
        "Import bill data from Raspador Legislativo: "
        "https://github.com/cuducos/raspadorlegislativo"
    )
    model = Bill
    post_handle_cache = dict()

    def serialize(self, line):
        url = line["url"]
        keywords = set(
            keyword.strip().lower()[:255]
            for keyword in line["palavras_chave_originais"].split(",")
            if keyword
        )

        self.post_handle_cache[url] = line["autoria"]
        return Bill(
            summary=line["ementa"],
            name=line["nome"],
            keywords=tuple(keywords),
            source_id=line["id_site"],
            url=url,
        )

    def post_handle(self):
        kwargs = {"desc": "Linking authorship", "unit": "bills"}
        for url, authors in tqdm(self.post_handle_cache.items(), **kwargs):
            bill = Bill.objects.get(url=url)
            for author in authors.split(","):
                politician = get_politician(author.strip())
                if politician:
                    bill.authors.add(politician)
            bill.save()

        get_politician.cache_clear()
        self.post_handle_cache = None

        kwargs = {"desc": "Counting keywords", "unit": "politicians"}
        politicians = tuple(Politician.objects.exclude(bills=None))
        for politician in tqdm(politicians, **kwargs):
            counter = Counter()
            for bill in politician.bills.all():
                counter.update(bill.keywords)

            politician.bill_keywords = tuple(
                {"keyword": keyword, "total": total}
                for keyword, total in counter.most_common()
            )

        bulk_update(politicians, update_fields=("bill_keywords",))

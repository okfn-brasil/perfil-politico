from functools import lru_cache

from django.db.models import Q
from tqdm import tqdm

from perfil.core.management.commands import BaseCommand
from perfil.core.models import Bill, Candidate, Politician


@lru_cache(maxsize=1024)
def get_politician(name, post=None):
    name = name.upper()

    def get_match(qs, post=None):
        if post:
            qs = qs.filter(post=post)

        qs = (
            qs.exclude(politician_id=None)
            .values("politician_id")
            .order_by("-politician_id")
            .distinct()
        )
        matches = tuple(qs)

        if len(matches) != 1:  # cannot find a single match
            return None

        match, *_ = matches
        return Politician.objects.get(pk=match["politician_id"])

    qs = Candidate.objects.filter(Q(ballot_name=name) | Q(name=name))
    match = get_match(qs, post=post)

    if not match:
        qs = Candidate.objects.all()
        for word in name.split():
            if len(word) <= 3:
                continue
            qs = qs.filter(Q(ballot_name__contains=word) | Q(name__contains=word))

        match = get_match(qs, post=post)

    return match


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

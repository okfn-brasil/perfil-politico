from functools import lru_cache
from itertools import chain, product
from urllib.request import urlopen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import resolve_url
from tqdm import tqdm

from perfil.core.models import Candidate
from perfil.core.views import Stats


@lru_cache(maxsize=256)
def distinct(field, reversed=False):
    order_by = field if not reversed else f"-{field}"
    qs = Candidate.objects.values(field).distinct(field).order_by(order_by)
    return tuple(row[field] for row in qs)


class Command(BaseCommand):
    help = "Cache API endpoints for a given year"

    @property
    def default_domain(self):
        first_domain, *_ = settings.ALLOWED_HOSTS
        return first_domain

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument(
            "--domain",
            "-d",
            help=f"Application domain (default: {self.default_domain})",
            default=self.default_domain,
        )
        parser.add_argument("--https", "-s", help="Use HTTPS", action="store_true")

    @property
    def candidate_list_paths(self):
        states = (state.lower() for state in distinct("state"))
        posts = (post.lower().replace(" ", "-") for post in distinct("post"))
        for state, post in product(states, posts):
            yield resolve_url("api_candidate_list", self.year, state, post)

    @property
    def national_stats_paths(self):
        posts = (post.lower().replace(" ", "-") for post in Stats.NATIONAL_POSTS)
        combinations = product(posts, Stats.CHARACTERISTICS)
        for post, characteristic in combinations:
            yield resolve_url(
                "api_national_stats", self.stats_year, post, characteristic
            )

    @property
    def state_stats_paths(self):
        posts = (post.lower().replace(" ", "-") for post in Stats.NATIONAL_POSTS)
        states = (state.lower() for state in distinct("state") if state != "BR")
        combinations = product(states, posts, Stats.CHARACTERISTICS)
        for state, post, characteristic in combinations:
            yield resolve_url(
                "api_state_stats", state, self.stats_year, post, characteristic
            )

    def handle(self, *args, **options):
        self.year, domain = options.get("year"), options.get("domain")
        protocol = "https" if options.get("https") else "http"
        self.stats_year = self.year - 4

        paths = tuple(
            chain(
                self.candidate_list_paths,
                self.national_stats_paths,
                self.state_stats_paths,
            )
        )
        for path in tqdm(paths, unit="endpoints cached"):
            urlopen(f"{protocol}://{domain}{path}")

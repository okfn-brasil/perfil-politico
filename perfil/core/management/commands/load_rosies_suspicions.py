import asyncio
import json
from collections import defaultdict
from functools import lru_cache

import aiohttp
import requests
from django.core.management.base import BaseCommand
from django_bulk_update.helper import bulk_update
from tqdm import tqdm

from perfil.core.management.commands import get_politician


class Command(BaseCommand):

    help = "Load Rosie's suspicions from Jarbas API"

    api_url = (
        "https://jarbas.serenata.ai"
        "/api/chamber_of_deputies/reimbursement/"
        "?format=json&limit={}&offset={}&suspicions=1"
    )
    human_url = "https://jarbas.serenata.ai/layers/#/documentId/{}"

    semaphore = asyncio.BoundedSemaphore(8)
    labels = {
        "election_expenses": "Gasto com campanha eleitoral",
        "invalid_cnpj_cpf": "CNPJ ou CPF inválido",
        "irregular_companies_classifier": "CNPJ inativo",
        "meal_price_outlier": "Refeição superfaturada",
        "over_monthly_subquota_limit": "Gastos superior ao teto da sub-cota",
        "suspicious_traveled_speed_day": "Gastos em diversas cidades no mesmo dia",
    }

    @property
    def suspicions_stats(self):
        if hasattr(self, "_suspicions_stats"):
            return self._suspicions_stats

        url = self.api_url.format("", "")
        data = requests.get(url).json()
        self._suspicions_stats = data["count"], len(data["results"])
        return self.suspicions_stats

    @property
    def total_suspicions(self):
        return self.suspicions_stats[0]

    @property
    def suspicions_per_page(self):
        return self.suspicions_stats[1]

    def serialize(self, reimbursement):
        value = reimbursement["total_net_value"]
        url = self.human_url.format(reimbursement["document_id"])
        name = reimbursement["congressperson_name"]
        for key in reimbursement["suspicions"].keys():
            yield name, {"suspicion": self.labels.get(key), "value": value, "url": url}

    async def fetch(self, url):
        async with self.semaphore, self.session.get(url) as response:
            return await response.json()

    async def fetch_all(self):
        kwargs = {
            "desc": "Downloading Rosie's suspicions from Jarbas API",
            "unit": "suspicions",
            "total": self.total_suspicions,
        }
        with tqdm(**kwargs) as progress_bar:
            async with aiohttp.ClientSession() as session:
                self.session = session
                offsets = range(0, self.total_suspicions, self.suspicions_per_page)
                for offset in offsets:
                    url = self.api_url.format(self.suspicions_per_page, offset)
                    data = await self.fetch(url)
                    for reimbursement in data["results"]:
                        self._suspicions.extend(self.serialize(reimbursement))
                        progress_bar.update(1)

    @property
    def suspicions(self):
        if hasattr(self, "_suspicions"):
            return self._suspicions

        self._suspicions = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_all())
        return self._suspicions

    @property
    def suspicions_by_politician(self):
        if hasattr(self, "_suspicions_by_politician"):
            return self._suspicions_by_politician

        self._suspicions_by_politician = defaultdict(list)
        for name, suspicion in self.suspicions:
            self._suspicions_by_politician[name].append(suspicion)
        return self.suspicions_by_politician

    @property
    def updated_politicians(self):
        kwargs = {
            "total": len(self.suspicions_by_politician),
            "unit": "politicians",
            "desc": "Linking suspicions to politicians",
        }
        for name, suspicions in tqdm(self.suspicions_by_politician.items(), **kwargs):
            politician = get_politician(name)
            if not politician:
                continue

            current_suspicions_urls = set(
                suspicion["url"] for suspicion in politician.rosies_suspicions
            )
            for suspicion in suspicions:
                if suspicion["url"] not in current_suspicions_urls:
                    politician.rosies_suspicions.append(suspicion)

            yield politician

    def handle(self, *args, **options):
        bulk_update(self.updated_politicians, update_fields=("rosies_suspicions",))

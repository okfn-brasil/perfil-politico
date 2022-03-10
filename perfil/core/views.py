import statistics
from collections import defaultdict

from cached_property import cached_property
from django.db import connection
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from restless.dj import DjangoResource
from restless.preparers import CollectionSubPreparer, FieldsPreparer

from perfil.core.models import (
    STATES,
    Candidate,
    age,
    ElectionIncomeStatement,
    PreCalculatedStats,
)


def home(request):
    return JsonResponse({"message": "API do Perfil Politico está online."})


class CandidateListResource(DjangoResource):
    preparer = FieldsPreparer(
        fields={
            "id": "id",
            "name": "ballot_name",
            "party": "party.abbreviation",
            "state": "state",
            "post": "post",
            "image": "image",
            "gender": "gender",
            "ethnicity": "ethnicity",
            "elections": "elections",
            "elections_won": "elections_won",
        }
    )

    @cached_property
    def api_fields(self):
        """Define fields to select in the QuerySet based on preparer fields"""
        fields = ["year", "sequential"]
        methods = {"elections_won", "image"}

        for field in self.preparer.fields.values():
            if field in methods:
                continue

            if field == "elections":
                field = "politician__election_history"

            fields.append(field.replace(".", "__"))

        return tuple(fields)

    def list(self, year, state, post):
        state = state.upper()
        post = post.upper().replace("-", " ")
        return (
            Candidate.objects.campaign(year)
            .filter(post=post, state=state)
            .select_related("party", "politician")
            .only(*self.api_fields)
        )


class CandidateDetailResource(DjangoResource):
    bill_preparer = FieldsPreparer(
        fields={"name": "name", "keywords": "keywords", "url": "url"}
    )

    preparer = FieldsPreparer(
        fields={
            "id": "id",
            "name": "name",
            "image": "image",
            "ballot_name": "ballot_name",
            "ballot_number": "number",
            "city": "politician.current_affiliation.city.name",
            "state": "state",
            "party": "party.name",
            "party_abbreviation": "party.abbreviation",
            "affiliation_history": "affiliation_history",
            "asset_history": "asset_history",
            "elections": "elections",
            "elections_won": "elections_won",
            "election_history": "election_history",
            "date_of_birth": "date_of_birth",
            "city_of_birth": "place_of_birth.name",
            "state_of_birth": "place_of_birth.state",
            "gender": "gender",
            "email": "email",
            "age": "get_age",
            "ethnicity": "ethnicity",
            "marital_status": "marital_status",
            "education": "education",
            "nationality": "nationality",
            "occupation": "occupation",
            "post": "post",
            "post_code": "post_code",
            "number": "number",
            "coalition_name": "coalition_name",
            "coalition_description": "coalition_description",
            "coalition_short_name": "coalition_short_name",
            "bills": CollectionSubPreparer("bills", bill_preparer),
            "bill_keywords": "bill_keywords",
            "rosies_suspicions": "rosies_suspicions",
        }
    )

    @cached_property
    def api_fields(self):
        """Define fields to select in the QuerySet based on preparer fields"""
        fields = ["year", "sequential"]
        methods = {
            "elections",
            "elections_won",
            "image",
            "get_age",
            "rosies_suspicions",
        }

        for field in self.preparer.fields.values():
            if field in methods or not isinstance(field, str):
                continue

            if field == "election_history":
                field = "politician__election_history"

            if field == "affiliation_history":
                field = "politician__affiliation_history"

            if field == "asset_history":
                field = "politician__asset_history"

            if field == "bill_keywords":
                field = "politician__bill_keywords"

            fields.append(field.replace(".", "__"))

        return tuple(fields)

    def detail(self, pk):
        return (
            Candidate.objects.select_related("party", "politician", "place_of_birth")
            .only(*self.api_fields)
            .get(pk=pk)
        )


class CandidateEconomicBonds:
    @staticmethod
    def build_company_cnpj(company: dict):
        return f"{company.get('cnpj_raiz', '')}{company.get('cnpj_ordem', '')}{company.get('cnpj_dv', '')}"

    @staticmethod
    def get_companies_with_participation(candidate: Candidate) -> list:
        return [
            {
                "cnpj": CandidateEconomicBonds.build_company_cnpj(company),
                "company_name": company.get("nome_empresa"),
                "main_cnae": str(company.get("cnae_principal"))
                if company.get("cnae_principal")
                else None,
                "secondary_cnaes": company.get("cnae_secundaria"),
                "uf": company.get("uf"),
                "foundation_date": company.get("data_inicio_atividade"),
                "participation_start_date": company.get("data_entrada_sociedade"),
            }
            for company in candidate.owned_companies
        ]

    @staticmethod
    def get_electoral_income_history(candidate: Candidate) -> list:
        if candidate.sequential and candidate.taxpayer_id:
            income_statements = ElectionIncomeStatement.objects.filter(
                Q(accountant_sequential=candidate.sequential)
                | Q(accountant_taxpayer_id=candidate.taxpayer_id)
            )
        elif candidate.sequential:
            income_statements = ElectionIncomeStatement.objects.filter(
                accountant_sequential=candidate.sequential
            )
        elif candidate.taxpayer_id:
            income_statements = ElectionIncomeStatement.objects.filter(
                accountant_taxpayer_id=candidate.taxpayer_id
            )
        else:
            return []
        return sorted(
            [
                {
                    "year": int(statement.year),
                    "value": float(statement.value),
                    "donor_name": statement.donor_name,
                    "donor_taxpayer_id": statement.donor_taxpayer_id,
                    "donor_company_name": statement.additional_income_information.get(
                        "nome_empresa"
                    ),
                    "donor_company_cnpj": CandidateEconomicBonds.build_company_cnpj(
                        statement.additional_income_information
                    ),
                    "donor_economic_sector_code": str(
                        statement.additional_income_information.get("cnae_principal")
                        or statement.donor_economic_sector_code
                    ),
                    "donor_secondary_sector_codes": statement.additional_income_information.get(
                        "cnae_secundaria"
                    ),
                }
                for statement in income_statements.all()
            ],
            key=lambda item: item["year"],
        )

    def get(self, request, pk):
        try:
            candidate = Candidate.objects.get(pk=pk)
        except Candidate.DoesNotExist:
            raise Http404(f"Candidate with pk ({pk}) not found.")

        income_history = self.get_electoral_income_history(candidate)
        companies_with_participation = self.get_companies_with_participation(candidate)

        return JsonResponse(
            {
                "election_income_history": income_history,
                "companies_associated_with_politician": companies_with_participation,
            },
            safe=False,
        )


class Stats:
    """Base class that supports stats views"""

    STATES = set(abbreviation.upper() for abbreviation, _ in STATES)

    NATIONAL_POSTS = {
        "DEPUTADO DISTRITAL",
        "DEPUTADO ESTADUAL",
        "DEPUTADO FEDERAL",
        "GOVERNADOR",
        "PREFEITO",
        "SENADOR",
        "VEREADOR",
    }

    CHARACTERISTICS = {
        "age",
        "education",
        "ethnicity",
        "gender",
        "marital_status",
        "occupation",
        "party",
        "post",
    }

    @staticmethod
    def validate_argument(argument, choices):
        if argument not in choices:
            valid_choices = ", ".join(choices)
            msg = f"{argument} is invalid. Try one of those: {valid_choices}"
            raise Http404(msg)

    @staticmethod
    def validate_arguments(arguments: list, choices):
        for argument in arguments:
            Stats.validate_argument(argument, choices)


class AssetStats(Stats):
    """Class that supports the candidates assets stats views"""

    def __init__(self, states=None, posts=None):
        self.states = [state.upper() for state in (states or [])]
        self.posts = [post.replace("-", " ").upper() for post in (posts or [])]

        self.validate_arguments(self.posts, self.NATIONAL_POSTS)
        self.validate_arguments(self.states, self.STATES)

    def _build_states_filter(self):
        if len(self.states) == 1:
            return f"core_candidate.state='{self.states[0]}'"
        return f"core_candidate.state IN {tuple(self.states)}"

    def _build_posts_filter(self):
        if len(self.posts) == 1:
            return f"core_candidate.post='{self.posts[0]}'"
        return f"core_candidate.post IN {tuple(self.posts)}"

    def _calculate_assets_median_for_specific_group(self) -> list:
        query_filter = "core_candidate.round_result LIKE 'ELEIT%'"
        if self.states:
            states_filter = self._build_states_filter()
            query_filter = f"{query_filter} AND {states_filter}"
        if self.posts:
            posts_filter = self._build_posts_filter()
            query_filter = f"{query_filter} AND {posts_filter}"

        sql = f"""
            SELECT
                core_candidate.year,
                array_agg(core_asset.value) as assets_values
            FROM core_asset
            INNER JOIN core_candidate
            ON core_candidate.id = core_asset.candidate_id
            WHERE {query_filter}
            GROUP BY core_candidate.year;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return [
                {"year": year, "value": float(statistics.median(values))}
                for year, values in cursor.fetchall()
            ]

    @staticmethod
    def _get_pre_calculated_assets_median() -> list:
        stats = PreCalculatedStats.objects.filter(
            type=PreCalculatedStats.ASSETS_MEDIAN
        ).order_by("year")
        return [{"year": item.year, "value": float(item.value)} for item in stats]

    def __call__(self):
        assets_median = (
            self._get_pre_calculated_assets_median()
            if not (self.states or self.posts)
            else self._calculate_assets_median_for_specific_group()
        )

        return JsonResponse({"mediana_patrimonios": assets_median})


class CandidateCharacteristicsStats(Stats):
    """Class that supports the candidates characteristics stats views"""

    def __init__(self, year, post, characteristic, state=None):
        self.state = state.upper() if state else None
        self.year = year
        self.post = post.replace("-", " ").upper()
        self.characteristic = characteristic.lower()
        self.field = self.get_field_name(self.characteristic)

        self.validate_argument(self.post, self.NATIONAL_POSTS)
        self.validate_argument(self.characteristic, self.CHARACTERISTICS)
        if state:
            self.validate_argument(self.state, self.STATES)

    @staticmethod
    def get_field_name(characteristic):
        if characteristic == "age":
            return "date_of_birth"

        if characteristic == "party":
            return "party__abbreviation"

        return characteristic

    def age_stats(self, data):
        aggregated = defaultdict(int)
        ordered = (
            "less-than-25",
            "between-25-and-34",
            "between-35-and-44",
            "between-45-and-59",
            "between-60-and-69",
            "70-or-more",
        )

        def aggregate(date_of_birth):
            politician_age = age(date_of_birth, self.year)

            if politician_age < 25:
                return "less-than-25"
            if 25 <= politician_age < 35:
                return "between-25-and-34"
            if 35 <= politician_age < 45:
                return "between-35-and-44"
            if 45 <= politician_age < 60:
                return "between-45-and-59"
            if 60 <= politician_age < 70:
                return "between-60-and-69"
            return "70-or-more"

        for row in data:
            date_of_birth, total = row["characteristic"], row["total"]
            aggregated[aggregate(date_of_birth)] += total

        return tuple(
            {"characteristic": key, "total": aggregated[key]} for key in ordered
        )

    def __call__(self):
        qs = Candidate.objects.filter(
            year=self.year, post=self.post, round_result__startswith="ELEIT"
        )
        if self.state:
            qs = qs.filter(state=self.state)
        qs = qs.values(self.field).annotate(total=Count("id")).order_by("-total")
        data = [
            {"characteristic": row[self.field], "total": row["total"]} for row in qs
        ]

        if self.characteristic == "age":
            data = self.age_stats(data)

        return JsonResponse(data, safe=False)


def national_stats(request, year, post, characteristic):
    stats = CandidateCharacteristicsStats(year, post, characteristic)
    return stats()


def state_stats(request, state, year, post, characteristic):
    stats = CandidateCharacteristicsStats(year, post, characteristic, state)
    return stats()


def asset_stats(request):
    states = request.GET.getlist("state", [])
    posts = request.GET.getlist("candidate_post", [])

    stats = AssetStats(states=states, posts=posts)
    return stats()

import statistics
from django.db import connection
from django.core.management.base import BaseCommand

from perfil.core.models import PreCalculatedStats


class Command(BaseCommand):
    help = "Pre calculate statistics over the politicians data to retrieve them faster"

    model = PreCalculatedStats

    @staticmethod
    def _get_assets_median_per_year() -> dict:
        sql = f"""
            SELECT
                core_candidate.year,
                array_agg(core_asset.value) as assets_values
            FROM core_asset
            INNER JOIN core_candidate
            ON core_candidate.id = core_asset.candidate_id
            WHERE core_candidate.round_result LIKE 'ELEIT%'
            GROUP BY core_candidate.year;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return {
                year: statistics.median(values) for year, values in cursor.fetchall()
            }

    def handle(self, *args, **options):
        print("-> Collecting data...")
        medians = self._get_assets_median_per_year()
        print(f"medians: {medians}")
        print("-> Storing data...")
        stats_to_save = []
        for year, median in medians.items():
            stats_to_save.append(
                self.model(
                    type=self.model.ASSETS_MEDIAN,
                    year=year,
                    value=median,
                    description="Mediana do valor do patrimônio de deputados eleitos em dado ano.",
                )
            )

        self.model.objects.bulk_create(stats_to_save)
        print("-> Just finished :)")

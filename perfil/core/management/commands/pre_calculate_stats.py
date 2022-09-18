import statistics
from django.db import connection

from perfil.core.management.commands import BaseCommand
from perfil.core.models import PreCalculatedStats


class Command(BaseCommand):
    help = "Pre calculate statistics over the politicians data to retrieve them faster"

    model = PreCalculatedStats

    def serialize(self, line):
        pass

    def post_handle(self):
        pass

    def add_arguments(self, parser):
        pass

    @staticmethod
    def _get_assets_median_per_year() -> dict:
        sql = f"""
            SELECT
              candidate_result.year,
              array_agg(assets_per_year_per_candidate.asset_values_sum) as assets_sum_per_candidate
            FROM core_candidate as candidate_result
            INNER JOIN (
              SELECT
                candidate_first_entry.year,
                candidate_first_entry.id,
                candidate_first_entry.sequential,
                candidate_first_entry.voter_id,
                sum(core_asset.value) as asset_values_sum
              FROM
                core_asset
              LEFT JOIN core_candidate as candidate_first_entry
              ON candidate_first_entry.id = core_asset.candidate_id
              GROUP BY
                candidate_first_entry.year,
                candidate_first_entry.id,
                candidate_first_entry.sequential,
                candidate_first_entry.voter_id
            ) as assets_per_year_per_candidate
            ON
              (candidate_result.sequential = assets_per_year_per_candidate.sequential)
              AND (candidate_result.voter_id = assets_per_year_per_candidate.voter_id)
              AND (candidate_result.year = assets_per_year_per_candidate.year)
            WHERE
              candidate_result.round_result LIKE 'ELEIT%'
            GROUP BY
              candidate_result.year;
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return {
                year: statistics.median(values) for year, values in cursor.fetchall()
            }

    def handle(self, *args, **options):
        self.delete_all_objects()
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

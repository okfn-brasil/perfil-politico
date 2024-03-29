# Generated by Django 3.2.5 on 2021-10-17 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_alter_affiliation_electoral_section"),
    ]

    operations = [
        migrations.CreateModel(
            name="PreCalculatedStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("AssetsMedian", "AssetsMedian")], max_length=15
                    ),
                ),
                ("year", models.IntegerField()),
                ("value", models.DecimalField(decimal_places=2, max_digits=16)),
                ("description", models.CharField(max_length=255, null=True)),
            ],
        ),
    ]

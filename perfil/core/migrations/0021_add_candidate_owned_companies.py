# Generated by Django 3.2.5 on 2021-11-27 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_create_election_income_statement"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidate",
            name="owned_companies",
            field=models.JSONField(default=list),
        ),
    ]

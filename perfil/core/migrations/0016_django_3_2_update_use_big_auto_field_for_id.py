# Generated by Django 3.2.5 on 2021-07-13 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_add_rosies_suspicions_field_to_politician"),
    ]

    operations = [
        migrations.AlterField(
            model_name="affiliation",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="bill",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="candidate",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="city",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="party",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="politician",
            name="affiliation_history",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="politician",
            name="asset_history",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="politician",
            name="bill_keywords",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="politician",
            name="election_history",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="politician",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="politician",
            name="rosies_suspicions",
            field=models.JSONField(default=list),
        ),
    ]

# Generated by Django 3.2.5 on 2022-09-12 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_alter_affiliation_electoral_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='code',
            field=models.IntegerField(null=True),
        ),
    ]
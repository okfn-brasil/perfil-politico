from django.db import models

from utils.infos import STATES


class Person(models.Model):
    civil_name = models.CharField(max_length=250)
    cpf = models.CharField(max_length=14)
    gender = models.CharField(max_length=250)
    voter_id = models.CharField(max_length=250)
    birthday = models.CharField(max_length=250)
    birthdate = models.DateField(max_length=250, null=True)
    birthplace_city = models.CharField(max_length=250)
    birthplace_state = models.CharField(max_length=2, choices=STATES)
    occupation = models.CharField(max_length=250)

    def __str__(self):
        return self.civil_name

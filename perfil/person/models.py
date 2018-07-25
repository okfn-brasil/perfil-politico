from django.db import models

from perfil.utils.infos import STATES


class Person(models.Model):
    civil_name = models.CharField(max_length=250)
    cpf = models.CharField(max_length=14, unique=True)
    gender = models.CharField(max_length=250, blank=True)
    voter_id = models.CharField(max_length=250, blank=True)
    birthday = models.CharField(max_length=250, blank=True)
    birthdate = models.DateField(max_length=250, null=True)
    birthplace_city = models.CharField(max_length=250, blank=True)
    birthplace_state = models.CharField(max_length=2, choices=STATES,
                                        blank=True)
    occupation = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.civil_name

    class Meta:
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['civil_name', 'birthdate']),
        ]

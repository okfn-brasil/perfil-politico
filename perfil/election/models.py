from django.db import models

from perfil.party.models import Party
from perfil.person.models import Person
from .choices import ELECTION_RESULT, POSITIONS, TYPE_OF_ASSET


class Election(models.Model):
    candidate = models.ForeignKey(Person, on_delete=models.CASCADE,
                                  related_name='elections')
    candidate_sequential = models.CharField(max_length=50)
    legend_composition = models.CharField(max_length=250)
    legend_name = models.CharField(max_length=250)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    place = models.CharField(max_length=250)
    position = models.CharField(max_length=2, choices=POSITIONS)
    result = models.CharField(max_length=1, choices=ELECTION_RESULT)
    state = models.CharField(max_length=250)
    year = models.IntegerField()

    def __str__(self):
        return f'{self.candidate.civil_name} - {self.year} - {self.position}'


class Donation(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    donator = models.CharField(max_length=250)
    donator_id = models.CharField(max_length=14, default='', blank=True)
    original_donator = models.CharField(max_length=250, default='', blank=True)
    original_donator_id = models.CharField(max_length=14, default='', blank=True)
    date = models.DateField(null=True)
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    description = models.CharField(max_length=250, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['donator_id']),
            models.Index(fields=['value'])
        ]


class Asset(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE,
                                 related_name='assets')
    description = models.CharField(max_length=250, blank=True)
    type = models.CharField(max_length=2, choices=TYPE_OF_ASSET)
    value = models.FloatField()

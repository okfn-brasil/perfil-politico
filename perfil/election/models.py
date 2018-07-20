from django.db import models

from party.models import Party
from person.models import Person


class Election(models.Model):
    year = models.IntegerField()
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    position = models.CharField(max_length=250)
    legend_name = models.CharField(max_length=250)
    legend_composition = models.CharField(max_length=250)
    result = models.CharField(max_length=250)
    candidate = models.ForeignKey(Person, on_delete=models.CASCADE)
    place = models.CharField(max_length=250)
    state = models.CharField(max_length=250)

    def __str__(self):
        return '{} - {} - {}'.format(self.candidate.civil_name,
                                     self.year,
                                     self.position)

from django.db import models

from perfil.party.models import Party
from perfil.person.models import Person


class Politician(models.Model):
    congressperson_id = models.CharField(max_length=250)
    congressperson_name = models.CharField(max_length=250)
    congressperson_bio = models.URLField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'politicians'
        indexes = [
            models.Index(fields=['congressperson_id']),
            models.Index(fields=['congressperson_name']),
        ]


class Term(models.Model):
    number = models.IntegerField()
    begin = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    position = models.CharField(max_length=250)
    region = models.CharField(max_length=250)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'terms'
        indexes = [
            models.Index(fields=['position']),
        ]


class Activity(models.Model):
    area = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    position = models.CharField(max_length=250)
    begin = models.IntegerField()
    end = models.IntegerField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'activities'
        indexes = [
            models.Index(fields=['position']),
        ]


class PartyFiliation(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE,
                               related_name='filiations')

from django.db import models

from perfil.party.models import Party
from perfil.person.models import Person


class Politician(models.Model):
    # TODO: add information from where the ID is from (deputy/senate)
    congressperson_id = models.CharField(max_length=250, unique=True)
    congressperson_name = models.CharField(max_length=250)
    congressperson_bio = models.URLField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    twitter = models.CharField(max_length=250)
    second_twitter = models.CharField(max_length=250)
    facebook = models.CharField(max_length=250)

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


class Tweet(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE,
                                   related_name='tweets')
    url = models.CharField(max_length=250)
    num_retweets = models.PositiveIntegerField()
    num_replys = models.PositiveIntegerField()
    num_favorites = models.PositiveIntegerField()
    text = models.TextField()
    is_reply = models.BooleanField()
    is_retweet = models.BooleanField()
    twitter_id = models.BigIntegerField()

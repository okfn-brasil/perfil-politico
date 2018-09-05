from collections import Counter

from django.contrib.postgres.fields import ArrayField
from django.db import models

from perfil.mandate.choices import POLITIC_AREA
from perfil.party.models import Party
from perfil.person.models import Person
from perfil.utils.text import prepare_string, INVALID_WORDS


class Politician(models.Model):
    area = models.CharField(max_length=2, choices=POLITIC_AREA, default="1")
    congressperson_id = models.CharField(max_length=250)
    congressperson_name = models.CharField(max_length=250)
    congressperson_bio = models.URLField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    twitter = models.CharField(max_length=250)
    second_twitter = models.CharField(max_length=250)
    facebook = models.CharField(max_length=250)

    class Meta:
        unique_together = ("congressperson_id", "area")
        verbose_name_plural = "politicians"
        indexes = [
            models.Index(fields=["congressperson_id"]),
            models.Index(fields=["congressperson_name"]),
        ]

    def get_bills_keywords(self):
        keywords =[]
        for bill in self.bill_set.all():
            keywords.extend(bill.original_keywords)
        return keywords

    def count_bills_keywords(self):
        return Counter(self.get_bills_keywords())

    def get_twitter_words(self):
        values = self.tweets.values_list('text', flat=True)
        tweets_by_words = [prepare_string(text).split(' ') for text in values]

        words = []
        for text in tweets_by_words:
            for word in text:
                if word and word not in INVALID_WORDS:
                    words.append(word)
        return words

    def count_twitter_keywords(self):
        return Counter(k for k in self.get_twitter_words())


class Term(models.Model):
    number = models.IntegerField()
    begin = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    position = models.CharField(max_length=250)
    region = models.CharField(max_length=250)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "terms"
        indexes = [models.Index(fields=["position"])]


class Activity(models.Model):
    area = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    position = models.CharField(max_length=250)
    begin = models.IntegerField()
    end = models.IntegerField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "activities"
        indexes = [models.Index(fields=["position"])]


class PartyFiliation(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="filiations"
    )


class Tweet(models.Model):
    politician = models.ForeignKey(
        Politician, on_delete=models.CASCADE, related_name="tweets"
    )
    url = models.CharField(max_length=250)
    num_retweets = models.PositiveIntegerField()
    num_replys = models.PositiveIntegerField()
    num_favorites = models.PositiveIntegerField()
    text = models.TextField()
    is_reply = models.BooleanField()
    is_retweet = models.BooleanField()
    twitter_id = models.BigIntegerField()


class Bill(models.Model):
    date = models.DateField()
    authors = models.ManyToManyField(Politician)
    text = models.TextField()
    url_id = models.IntegerField()
    area = models.TextField()
    name = models.CharField(max_length=250)
    keywords = ArrayField(models.CharField(max_length=250))
    original_keywords = ArrayField(models.CharField(max_length=250))
    url = models.URLField(max_length=500)


class ClaimedIndemnification(models.Model):
    cnpj_cpf = models.CharField(max_length=14)
    supplier = models.CharField(max_length=255)
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    claim_id = models.CharField(max_length=255, blank=True, default="")
    month = models.IntegerField()
    year = models.IntegerField()
    category = models.CharField(max_length=255, blank=True, default="")
    sub_category = models.CharField(max_length=255, blank=True, default="")
    date = models.DateField(null=True)
    value = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "claimed indemnification"
        verbose_name_plural = "claimed indemnifications"
        indexes = [
            models.Index(fields=["cnpj_cpf"]),
            models.Index(fields=["month"]),
            models.Index(fields=["year", "month"]),
            models.Index(fields=["date"]),
        ]

from django.db import models

from perfil.utils.infos import STATES, GENDER_CHOICES


class Person(models.Model):
    civil_name = models.CharField(max_length=250)
    cpf = models.CharField(max_length=14, unique=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)
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
        verbose_name_plural = 'people'
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['civil_name', 'birthdate']),
        ]

    @property
    def election_parties(self):
        parties = [x[0] for x in self.elections.values_list('party__initials')]
        return list(set(parties))

    @property
    def filiation_parties(self):
        parties = [x[0] for x in self.filiations.values_list('party__initials')]
        return list(set(parties))

    @property
    def asset_evolution(self):
        election_assets = dict()
        for election in self.elections.all():
            total = sum([x[0] for x in election.assets.values_list('value')])
            election_assets[election.year] = total
        return election_assets

    @property
    def biggest_asset_evolution(self):
        if not self.asset_evolution:
            return 0
        max_key = max(self.asset_evolution,
                      key=lambda k: self.asset_evolution[k])
        return self.asset_evolution[max_key]


class PersonInformation(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    num_of_elections = models.IntegerField()
    num_of_elections_won = models.IntegerField()
    num_of_elections_won_by_quota = models.IntegerField()
    biggest_asset_evolutions = models.FloatField()
    total_parties_changed = models.IntegerField()
    election_parties = models.CharField(max_length=200)
    filiation_parties = models.CharField(max_length=200)

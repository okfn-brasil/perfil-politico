from django.db import models


class Party(models.Model):
    initials = models.CharField(unique=True, max_length=250)
    name = models.CharField(max_length=250)

    def __str__(self):
        return '{} - {}'.format(self.initials, self.name)

    class Meta:
        verbose_name_plural = 'parties'

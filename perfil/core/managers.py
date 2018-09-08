from django.db import models


class CampaignQuerySet(models.QuerySet):
    def campaign(self, year):
        return self.filter(year=year)


CampaignManager = models.Manager.from_queryset(CampaignQuerySet)

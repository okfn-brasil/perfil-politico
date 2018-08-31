from django.contrib import admin

from .models import Asset, Election


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    ordering = ("-year",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    ordering = ("election",)

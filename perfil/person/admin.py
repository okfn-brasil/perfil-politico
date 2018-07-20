from django.contrib import admin

from election.models import Election
from .models import Person


class ElectionInline(admin.TabularInline):
    model = Election
    exclude = ['legend_name', 'legend_composition']

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [ElectionInline]
    ordering = ('civil_name',)

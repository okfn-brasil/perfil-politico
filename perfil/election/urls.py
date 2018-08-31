from django.urls import include, path

from perfil.election.api import ElectionByPositionResource

urlpatterns = [path("position/", include(ElectionByPositionResource.urls()))]

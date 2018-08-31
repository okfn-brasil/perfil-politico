from django.urls import include, path

from perfil.person.api import PersonResource

urlpatterns = [path("", include(PersonResource.urls()))]

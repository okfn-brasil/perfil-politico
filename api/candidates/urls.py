from django.urls import include, path

from . import views

urlpatterns = [
    path('person/', include(views.PersonResource.urls())),
]

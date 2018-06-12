from django.urls import include, path

from . import views

urlpatterns = [
    path('candidate/', include(views.CandidateResource.urls())),
    path('state/', include(views.StateResource.urls())),
]

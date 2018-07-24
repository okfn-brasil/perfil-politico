from django.urls import include, path

from . import views

urlpatterns = [
    path('candidate/cpf/', include(views.FindByCPFResource.urls())),
    path('candidate/name/', include(views.FindByNameResource.urls())),
    path('state/', include(views.StateResource.urls())),
]

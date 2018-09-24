"""perfil URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from perfil.core.views import (
    CandidateDetailResource,
    CandidateListResource,
    home,
    national_stats,
    state_stats,
)


urlpatterns = [
    path("", home, name="home"),
    path(
        "api/candidate/<int:year>/<str:state>/<str:post>/",
        CandidateListResource.as_list(),
        name="api_candidate_list",
    ),
    path(
        "api/candidate/<int:pk>/",
        CandidateDetailResource.as_detail(),
        name="api_candidate_detail",
    ),
    path(
        "api/stats/<str:state>/<int:year>/<str:post>/<str:characteristic>/",
        state_stats,
        name="api_state_stats",
    ),
    path(
        "api/stats/<int:year>/<str:post>/<str:characteristic>/",
        national_stats,
        name="api_national_stats",
    ),
]

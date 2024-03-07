from django.urls import include, path

from laces.test.example.views import kitchen_sink


urlpatterns = [
    path("", kitchen_sink),
    path("components/", include("laces.urls")),
]

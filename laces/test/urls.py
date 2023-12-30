from django.urls import path

from laces.test.example.views import kitchen_sink


urlpatterns = [
    path("", kitchen_sink),
]

from django.urls import path

from laces.test.example.views import component_response, kitchen_sink


urlpatterns = [
    path("", kitchen_sink, name="kitchen_sink"),
    path("component-response/", component_response, name="component_response"),
]

from django.urls import path

from laces.test.example.views import component_response, kitchen_sink, single_component


urlpatterns = [
    path("", kitchen_sink, name="kitchen_sink"),
    path("single-component/", single_component, name="single_component"),
    path("component-response/", component_response, name="component_response"),
]

from django.urls import path

from laces.views import serve


app_name = "laces"


urlpatterns = [path("<slug:component_slug>/", serve, name="serve")]

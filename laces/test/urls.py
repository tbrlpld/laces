from django.contrib import admin
from django.urls import path

from laces.test.home.views import home


urlpatterns = [
    path("", home),
    path("django-admin/", admin.site.urls),
]

from django.shortcuts import render

from laces.test.components import Heading


def home(request):
    heading = Heading()
    return render(
        request,
        template_name="home/home.html",
        context={"heading": heading},
    )

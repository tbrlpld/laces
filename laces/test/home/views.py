from django.shortcuts import render

from laces.test.components import StaticTemplate


def home(request):
    static_template = StaticTemplate()
    return render(
        request,
        template_name="home/home.html",
        context={"static_template": static_template},
    )

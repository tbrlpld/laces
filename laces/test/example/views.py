from django.shortcuts import render

from laces.test.example.components import (
    PassesFixedNameToContextComponent,
    RendersTemplateWithFixedContentComponent,
)


def home(request):
    fixed_content = RendersTemplateWithFixedContentComponent()
    passes_name = PassesFixedNameToContextComponent()
    return render(
        request,
        template_name="home/home.html",
        context={
            "fixed_content": fixed_content,
            "passes_name": passes_name,
        },
    )

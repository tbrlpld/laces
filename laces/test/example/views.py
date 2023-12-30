from django.shortcuts import render

from laces.test.example.components import (
    PassesFixedNameToContextComponent,
    RendersTemplateWithFixedContentComponent,
)


def kitchen_sink(request):
    fixed_content = RendersTemplateWithFixedContentComponent()
    passes_name = PassesFixedNameToContextComponent()
    return render(
        request,
        template_name="pages/kitchen-sink.html",
        context={
            "fixed_content": fixed_content,
            "passes_name": passes_name,
        },
    )

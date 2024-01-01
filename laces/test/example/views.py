from django.shortcuts import render

from laces.test.example.components import (
    PassesFixedNameToContextComponent,
    RendersTemplateWithFixedContentComponent,
    ReturnsFixedContentComponent,
)


def kitchen_sink(request):
    fixed_content_template = RendersTemplateWithFixedContentComponent()
    fixed_content_return = ReturnsFixedContentComponent()
    passes_name = PassesFixedNameToContextComponent()
    return render(
        request,
        template_name="pages/kitchen-sink.html",
        context={
            "fixed_content_template": fixed_content_template,
            "fixed_content_return": fixed_content_return,
            "passes_name": passes_name,
        },
    )

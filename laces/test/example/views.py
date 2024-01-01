from django.shortcuts import render

from laces.test.example.components import (
    DataclassAsDictToContextComponent,
    PassesFixedNameToContextComponent,
    PassesInstanceAttributeToContextComponent,
    RendersTemplateWithFixedContentComponent,
    ReturnsFixedContentComponent,
)


def kitchen_sink(request):
    fixed_content_template = RendersTemplateWithFixedContentComponent()
    fixed_content_return = ReturnsFixedContentComponent()
    passes_fixed_name = PassesFixedNameToContextComponent()
    passes_instance_attr_name = PassesInstanceAttributeToContextComponent(name="Bob")
    dataclass_attr_name = DataclassAsDictToContextComponent(name="Charlie")

    return render(
        request,
        template_name="pages/kitchen-sink.html",
        context={
            "fixed_content_template": fixed_content_template,
            "fixed_content_return": fixed_content_return,
            "passes_fixed_name": passes_fixed_name,
            "passes_instance_attr_name": passes_instance_attr_name,
            "dataclass_attr_name": dataclass_attr_name,
        },
    )

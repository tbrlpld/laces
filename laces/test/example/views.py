from django.shortcuts import render

from laces.test.example.components import (
    DataclassAsDictContextComponent,
    HeadingComponent,
    ParagraphComponent,
    PassesFixedNameToContextComponent,
    PassesInstanceAttributeToContextComponent,
    PassesNameFromParentContextComponent,
    RendersTemplateWithFixedContentComponent,
    ReturnsFixedContentComponent,
    SectionWithHeadingAndParagraphComponent,
)


def kitchen_sink(request):
    fixed_content_template = RendersTemplateWithFixedContentComponent()
    fixed_content_return = ReturnsFixedContentComponent()
    passes_fixed_name = PassesFixedNameToContextComponent()
    passes_instance_attr_name = PassesInstanceAttributeToContextComponent(name="Bob")
    dataclass_attr_name = DataclassAsDictContextComponent(name="Charlie")
    passes_name_from_parent_context = PassesNameFromParentContextComponent()
    section_with_heading_and_paragraph = SectionWithHeadingAndParagraphComponent(
        heading=HeadingComponent(text="Hello"),
        content=ParagraphComponent(text="World"),
    )

    return render(
        request,
        template_name="pages/kitchen-sink.html",
        context={
            "fixed_content_template": fixed_content_template,
            "fixed_content_return": fixed_content_return,
            "passes_fixed_name": passes_fixed_name,
            "passes_instance_attr_name": passes_instance_attr_name,
            "dataclass_attr_name": dataclass_attr_name,
            "passes_name_from_parent_context": passes_name_from_parent_context,
            "name": "Dan",
            "section_with_heading_and_paragraph": section_with_heading_and_paragraph,
        },
    )

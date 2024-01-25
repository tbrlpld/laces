from django.shortcuts import render

from laces.test.example.components import (
    BlockquoteComponent,
    DataclassAsDictContextComponent,
    HeadingComponent,
    ListSectionComponent,
    ParagraphComponent,
    PassesFixedNameToContextComponent,
    PassesInstanceAttributeToContextComponent,
    PassesNameFromParentContextComponent,
    PassesSelfToContextComponent,
    RendersTemplateWithFixedContentComponent,
    ReturnsFixedContentComponent,
    SectionWithHeadingAndParagraphComponent,
)


def kitchen_sink(request):
    """Render a page with all example components."""
    fixed_content_template = RendersTemplateWithFixedContentComponent()
    fixed_content_return = ReturnsFixedContentComponent()
    passes_fixed_name = PassesFixedNameToContextComponent()
    passes_instance_attr_name = PassesInstanceAttributeToContextComponent(name="Bob")
    passes_self = PassesSelfToContextComponent(name="Carol")
    dataclass_attr_name = DataclassAsDictContextComponent(name="Charlie")
    passes_name_from_parent_context = PassesNameFromParentContextComponent()
    section_with_heading_and_paragraph = SectionWithHeadingAndParagraphComponent(
        heading=HeadingComponent(text="Hello"),
        content=ParagraphComponent(text="World"),
    )
    list_section = ListSectionComponent(
        heading=HeadingComponent(text="Heading"),
        items=[
            ParagraphComponent(text="Item 1"),
            BlockquoteComponent(text="Item 2"),
            ParagraphComponent(text="Item 3"),
        ],
    )

    return render(
        request,
        template_name="pages/kitchen-sink.html",
        context={
            "fixed_content_template": fixed_content_template,
            "fixed_content_return": fixed_content_return,
            "passes_fixed_name": passes_fixed_name,
            "passes_instance_attr_name": passes_instance_attr_name,
            "passes_self": passes_self,
            "dataclass_attr_name": dataclass_attr_name,
            "passes_name_from_parent_context": passes_name_from_parent_context,
            "name": "Dan",  # Provide as an example of parent context.
            "section_with_heading_and_paragraph": section_with_heading_and_paragraph,
            "list_section": list_section,
        },
    )

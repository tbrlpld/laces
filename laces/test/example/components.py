"""
Examples of how components might be defined.

This is unlikely to be an exhaustive list of examples, but it should be enough to
demonstrate the basic concepts of how components work.
"""
from dataclasses import asdict, dataclass

from django.utils.html import format_html

from laces.components import Component


class RendersTemplateWithFixedContentComponent(Component):
    template_name = "components/hello-world.html"


class ReturnsFixedContentComponent(Component):
    def render_html(self, parent_context=None):
        return format_html("<h1>Hello World Return</h1>\n")


class PassesFixedNameToContextComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(self, parent_context=None):
        return {"name": "Alice"}


class PassesInstanceAttributeToContextComponent(Component):
    template_name = "components/hello-name.html"

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def get_context_data(self, parent_context=None):
        return {"name": self.name}


class PassesSelfToContextComponent(Component):
    template_name = "components/hello-self-name.html"

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def get_context_data(self, parent_context=None):
        return {"self": self}


@dataclass
class DataclassAsDictContextComponent(Component):
    template_name = "components/hello-name.html"

    name: str

    def get_context_data(self, parent_context=None):
        return asdict(self)


class PassesNameFromParentContextComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(self, parent_context):
        return {"name": parent_context["name"]}


class SectionWithHeadingAndParagraphComponent(Component):
    template_name = "components/section.html"

    def __init__(self, heading: "HeadingComponent", content: "ParagraphComponent"):
        super().__init__()
        self.heading = heading
        self.content = content

    def get_context_data(self, parent_context=None):
        return {
            "heading": self.heading,
            "content": self.content,
        }


class HeadingComponent(Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def render_html(self, parent_context=None):
        return format_html("<h2>{}</h2>\n", self.text)


class ParagraphComponent(Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def render_html(self, parent_context=None):
        return format_html("<p>{}</p>\n", self.text)


class ListSectionComponent(Component):
    template_name = "components/list-section.html"

    def __init__(self, heading: "HeadingComponent", items: "list[Component]"):
        super().__init__()
        self.heading = heading
        self.items = items

    def get_context_data(self, parent_context=None):
        return {
            "heading": self.heading,
            "items": self.items,
        }


class BlockquoteComponent(Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def render_html(self, parent_context=None):
        return format_html("<blockquote>{}</blockquote>\n", self.text)

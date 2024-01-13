"""
Examples of how components might be defined.

This is unlikely to be an exhaustive list of examples, but it should be enough to
demonstrate the basic concepts of how components work.
"""

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from django.utils.html import format_html

from laces.components import Component


if TYPE_CHECKING:
    from typing import Any, Dict, Optional

    from django.utils.safestring import SafeString

    from laces.typing import RenderContext


class RendersTemplateWithFixedContentComponent(Component):
    template_name = "components/hello-world.html"


class ReturnsFixedContentComponent(Component):
    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        return format_html("<h1>Hello World Return</h1>\n")


class PassesFixedNameToContextComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        return {"name": "Alice"}


class PassesInstanceAttributeToContextComponent(Component):
    template_name = "components/hello-name.html"

    def __init__(self, name: str, **kwargs: "Dict[str, Any]") -> None:
        super().__init__(**kwargs)
        self.name = name

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        return {"name": self.name}


class PassesSelfToContextComponent(Component):
    template_name = "components/hello-self-name.html"

    def __init__(self, name: str, **kwargs: "Dict[str, Any]") -> None:
        super().__init__(**kwargs)
        self.name = name

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        return {"self": self}


@dataclass
class DataclassAsDictContextComponent(Component):
    template_name = "components/hello-name.html"

    name: str

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        return asdict(self)


class PassesNameFromParentContextComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(self, parent_context: "RenderContext") -> "RenderContext":
        return {"name": parent_context["name"]}


class SectionWithHeadingAndParagraphComponent(Component):
    template_name = "components/section.html"

    def __init__(self, heading: "HeadingComponent", content: "ParagraphComponent"):
        super().__init__()
        self.heading = heading
        self.content = content

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        return {
            "heading": self.heading,
            "content": self.content,
        }


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


class HeadingComponent(Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        return format_html("<h2>{}</h2>\n", self.text)


class ParagraphComponent(Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        return format_html("<p>{}</p>\n", self.text)


class BlockquoteComponent(Component):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        return format_html("<blockquote>{}</blockquote>\n", self.text)

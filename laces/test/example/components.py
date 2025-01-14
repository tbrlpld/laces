"""
Examples of how components might be defined.

This is unlikely to be an exhaustive list of examples, but it should be enough to
demonstrate the basic concepts of how components work.
"""

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from django.utils.html import format_html

from laces.components import Component, register_servable


if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional

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
        """Return context data with fixed `name`."""
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
        """Return context data with `name` attribute."""
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
        """Return context data with `self`."""
        return {"self": self}


@dataclass
class DataclassAsDictContextComponent(Component):
    template_name = "components/hello-name.html"

    name: str

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        """Return context data with dataclass object as dict."""
        return asdict(self)


class PassesNameFromParentContextComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        """Return the `name` from the parent context as the only key in the data."""
        if not parent_context or "name" not in parent_context:
            return {}
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
        """Return context data with heading and content."""
        return {
            "heading": self.heading,
            "content": self.content,
        }


class ListSectionComponent(Component):
    template_name = "components/list-section.html"

    def __init__(self, heading: "HeadingComponent", items: "List[Component]") -> None:
        super().__init__()
        self.heading = heading
        self.items = items

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        """Return context data with heading and items."""
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


class MediaDefiningComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        """Return context data with fixed `name`."""
        return {"name": "Media"}

    class Media:
        css = {"all": ("component.css",)}
        js = ("component.js",)


class HeaderWithMediaComponent(Component):
    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        return format_html("<header>Header with Media</header>")

    class Media:
        css = {"all": ("header.css",)}
        js = ("header.js", "common.js")


class FooterWithMediaComponent(Component):
    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        return format_html("<footer>Footer with Media</footer>")

    class Media:
        css = {"all": ("footer.css",)}
        js = ("footer.js", "common.js")


# Servables


@register_servable("fixed-content-template")
class ServableWithFixedContentTemplateComponent(Component):
    template_name = "components/hello-world.html"


@register_servable("with-init-args")
class ServableWithInitilizerArgumentsComponent(Component):
    template_name = "components/hello-name.html"

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "RenderContext":
        return {"name": self.name}


@register_servable("int-adder")
class ServableIntAdderComponent(Component):
    def __init__(self, number: int) -> None:
        self.number = 0 + number


class CustomException(Exception):
    pass


@register_servable("with-custom-exception-init")
class ServableWithCustomExceptionInitializerComponent(Component):
    def __init__(self) -> None:
        raise CustomException

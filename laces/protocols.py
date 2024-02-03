from typing import TYPE_CHECKING, Protocol, Union


if TYPE_CHECKING:
    from typing import Any, Optional

    from django.forms.widgets import Media
    from django.template import Context
    from django.utils.safestring import SafeString


class HasRenderHtmlMethod(Protocol):
    def render_html(  # noqa: E704
        self,
        parent_context: "Optional[Union[Context, dict[str, Any]]]",
    ) -> "SafeString": ...


class HasRenderMethod(Protocol):
    def render(  # noqa: E704
        self,
    ) -> "SafeString": ...


Renderable = Union[HasRenderHtmlMethod, HasRenderMethod]


class HasMediaProperty(Protocol):
    @property
    def media(self) -> "Media": ...  # noqa: E704

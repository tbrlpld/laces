from typing import TYPE_CHECKING, List

from django import template as django_template
from django.forms.widgets import Media, MediaDefiningClass
from django.template import loader

from laces.typing import HasMediaProperty


if TYPE_CHECKING:
    from typing import Optional

    from django.template.backends.base import _EngineTemplate
    from django.utils.safestring import SafeString

    from laces.typing import RenderContext


class Component(metaclass=MediaDefiningClass):
    """
    A class that knows how to render itself.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/094834909d5c4b48517fd2703eb1f6d386572ffa/wagtail/admin/ui/components.py#L8-L22  # noqa: E501

    A component uses the `MetaDefiningClass` metaclass to add a `media` property, which
    allows the definitions of CSS and JavaScript assets that are associated with the
    component. This works the same as `Media` class used by Django forms.
    See also: https://docs.djangoproject.com/en/4.2/topics/forms/media/
    """

    template_name: str
    template_string: str

    def render_html(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "SafeString":
        """
        Return string representation of the object.

        Given a context dictionary from the calling template (which may be a
        `django.template.Context` object or a plain `dict` of context variables),
        returns the string representation to be rendered.

        This will be subject to Django's HTML escaping rules, so a return value
        consisting of HTML should typically be returned as a
        `django.utils.safestring.SafeString` instance.
        """
        context_data = self.get_context_data(parent_context)
        template = self.get_template()
        return template.render(context_data)

    def get_template(self) -> "_EngineTemplate":
        """
        Return the template object used to render the component.

        First attempts to find a template via the name returned to by
        `get_template_name`.

        If no valid template was found, use the template string returned by
        `get_template_string`. The string is interpreted by the first template engine.
        """
        if template_name := self.get_template_name():
            template = loader.get_template(template_name)
            return template

        if template_string := self.get_template_string():
            # Use the first engine to render the template string.
            # This is somewhat analogous to how `loader.get_template` works.
            # `loader.get_template` iterates through all the engines until the template
            # is found. Here, we only use the first, because we don't have a signal,
            # like a not-found error, to move on to the next one.
            engines = django_template.engines.all()
            first_engine = engines[0]
            template = first_engine.from_string(template_string)
            return template

        # TODO: Use a custom exception
        raise ValueError("No template defined for the component.")

    def get_template_name(self) -> "Optional[str]":
        """
        Return the name of the template used to render the component.

        Returns the `template_name` attribute of the component by default. You may
        override this method to return different templates depending on the component's
        state.

        Returns
        -------
        str | None
            Name of the template used to render the component. None if no template name
            is defined.
        """
        return getattr(self, "template_name", None)

    def get_template_string(self) -> "Optional[str]":
        """
        Return the template string to use when rendering the component.

        Returns the `template_string` attribute of the component by default. You may
        override this method to return different templates depending on the component's
        state.

        Returns
        -------
        str | None
            String of template code to render the component with. None if no template
            string was defined.
        """
        return getattr(self, "template_string", None)

    def get_context_data(
        self,
        parent_context: "Optional[RenderContext]" = None,
    ) -> "Optional[RenderContext]":
        """Return the context data to render this component with."""
        return {}

    # fmt: off
    if TYPE_CHECKING:
        # It's ugly, I know. But it seems to be the best way to make `mypy` happy.
        # The `media` property is dynamically added by the `MediaDefiningClass`
        # metaclass. Because of how dynamic it is, `mypy` is not able to pick it up.
        # This is why we need to add a type hint for it here. The other way would be a
        # stub, but that would require the whole module to be stubbed and that is even
        # more annoying to keep up to date.
        @property
        def media(self) -> Media: ...  # noqa: E704
    # fmt: on


class MediaContainer(List[HasMediaProperty]):
    """
    A list that provides a `media` property that combines the media definitions
    of its members.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/ca8a87077b82e20397e5a5b80154d923995e6ca9/wagtail/admin/ui/components.py#L25-L36  # noqa: E501

    The `MediaContainer` functionality depends on the `django.forms.widgets.Media`
    class. The `Media` class provides the logic to combine the media definitions of
    multiple objects through its `__add__` method. The `MediaContainer` relies on this
    functionality to provide a `media` property that combines the media definitions of
    its members.

    See also:
    https://docs.djangoproject.com/en/4.2/topics/forms/media
    """

    @property
    def media(self) -> Media:
        """
        Return a `Media` object containing the media definitions of all members.

        This makes use of the `Media.__add__` method, which combines the media
        definitions of two `Media` objects.

        """
        media = Media()
        for item in self:
            media += item.media
        return media

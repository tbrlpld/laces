from typing import Any, MutableMapping

from django.forms import Media, MediaDefiningClass
from django.template import Context
from django.template.loader import get_template


class Component(metaclass=MediaDefiningClass):
    """
    A class that knows how to render itself.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/094834909d5c4b48517fd2703eb1f6d386572ffa/wagtail/admin/ui/components.py#L8-L22  # noqa: E501
    """

    def get_context_data(
        self, parent_context: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        return {}

    def render_html(self, parent_context: MutableMapping[str, Any] = None) -> str:
        """
        Return string representation of the object.

        Given a context dictionary from the calling template (which may be a
        `django.template.Context` object or a plain ``dict`` of context variables),
        returns the string representation to be rendered.

        This will be subject to Django's HTML escaping rules, so a return value
        consisting of HTML should typically be returned as a
        `django.utils.safestring.SafeString` instance.
        """
        if parent_context is None:
            parent_context = Context()
        context_data = self.get_context_data(parent_context)
        if context_data is None:
            raise TypeError("Expected a dict from get_context_data, got None")

        template = get_template(self.template_name)
        return template.render(context_data)


class MediaContainer(list):
    """
    A list that provides a ``media`` property that combines the media definitions
    of its members.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/ca8a87077b82e20397e5a5b80154d923995e6ca9/wagtail/admin/ui/components.py#L25-L36  # noqa: E501
    """

    @property
    def media(self):
        media = Media()
        for item in self:
            media += item.media
        return media

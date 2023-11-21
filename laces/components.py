from typing import Any, MutableMapping

from django.forms import MediaDefiningClass
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
        if parent_context is None:
            parent_context = Context()
        context_data = self.get_context_data(parent_context)
        if context_data is None:
            raise TypeError("Expected a dict from get_context_data, got None")

        template = get_template(self.template_name)
        return template.render(context_data)

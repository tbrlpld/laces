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

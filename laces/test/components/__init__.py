from laces.components import Component


class RendersTemplateWithFixedContentComponent(Component):
    template_name = "components/hello-world.html"


class PassesFixedNameToContextComponent(Component):
    template_name = "components/hello-name.html"

    def get_context_data(self, parent_context=None):
        return {"name": "Alice"}

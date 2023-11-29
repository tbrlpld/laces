from django.template import Context, Template
from django.test import SimpleTestCase
from django.utils.html import format_html

from laces.components import Component


class TestComponentTag(SimpleTestCase):
    """
    Test for the `component` template tag.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/main/wagtail/admin/tests/test_templatetags.py#L225-L305  # noqa: E501
    """

    def test_passing_context_to_component(self):
        class MyComponent(Component):
            def render_html(self, parent_context):
                return format_html(
                    "<h1>{} was here</h1>", parent_context.get("first_name", "nobody")
                )

        template = Template(
            "{% load laces %}{% with first_name='Kilroy' %}{% component my_component %}{% endwith %}"
        )
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(html, "<h1>Kilroy was here</h1>")

        template = Template(
            "{% load laces %}{% component my_component with first_name='Kilroy' %}"
        )
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(html, "<h1>Kilroy was here</h1>")

        template = Template(
            "{% load laces %}{% with first_name='Kilroy' %}{% component my_component with surname='Silk' only %}{% endwith %}"
        )
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(html, "<h1>nobody was here</h1>")

    def test_fallback_render_method(self):
        class MyComponent(Component):
            def render_html(self, parent_context):
                return format_html("<h1>I am a component</h1>")

        class MyNonComponent:
            def render(self):
                return format_html("<h1>I am not a component</h1>")

        template = Template("{% load laces %}{% component my_component %}")
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(html, "<h1>I am a component</h1>")
        with self.assertRaises(ValueError):
            template.render(Context({"my_component": MyNonComponent()}))

        template = Template(
            "{% load laces %}{% component my_component fallback_render_method=True %}"
        )
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(html, "<h1>I am a component</h1>")
        html = template.render(Context({"my_component": MyNonComponent()}))
        self.assertEqual(html, "<h1>I am not a component</h1>")

    def test_component_escapes_unsafe_strings(self):
        class MyComponent(Component):
            def render_html(self, parent_context):
                return "Look, I'm running with scissors! 8< 8< 8<"

        template = Template("{% load laces %}<h1>{% component my_component %}</h1>")
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(
            html, "<h1>Look, I&#x27;m running with scissors! 8&lt; 8&lt; 8&lt;</h1>"
        )

    def test_error_on_rendering_non_component(self):
        template = Template("{% load laces %}<h1>{% component my_component %}</h1>")

        with self.assertRaises(ValueError) as cm:
            template.render(Context({"my_component": "hello"}))
        self.assertEqual(str(cm.exception), "Cannot render 'hello' as a component")

    def test_render_as_var(self):
        class MyComponent(Component):
            def render_html(self, parent_context):
                return format_html("<h1>I am a component</h1>")

        template = Template(
            "{% load laces %}{% component my_component as my_html %}The result was: {{ my_html }}"
        )
        html = template.render(Context({"my_component": MyComponent()}))
        self.assertEqual(html, "The result was: <h1>I am a component</h1>")

from unittest.mock import Mock

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

    def setUp(self):
        self.parent_template = Template("")

        class ExampleComponent(Component):
            pass

        self.component = ExampleComponent()
        # Using a mock to be able to check if the `render_html` method is called.
        self.component.render_html: Mock = Mock(return_value="Rendered HTML")

    def set_parent_template(self, template_string):
        template_string = "{% load laces %}" + template_string
        self.parent_template = Template(template_string)

    def render_parent_template_with_context(self, context: dict):
        return self.parent_template.render(Context(context))

    def assertRenderHTMLCalledWith(self, context: dict):
        self.assertTrue(self.component.render_html.called_with(Context(context)))

    def test_render_html_return_in_parent_template(self):
        self.set_parent_template("Before {% component my_component %} After")
        self.assertEqual(self.component.render_html(), "Rendered HTML")

        result = self.render_parent_template_with_context(
            {"my_component": self.component},
        )

        # This matches the return value of the `render_html` method.
        self.assertEqual(result, "Before Rendered HTML After")

    def test_render_html_parent_context_when_only_component_in_context(self):
        self.set_parent_template("{% component my_component %}")

        self.render_parent_template_with_context({"my_component": self.component})

        self.assertTrue(self.component.render_html.called)
        # The component itself is not included in the context that is passed to the
        # `render_html` method.
        self.assertRenderHTMLCalledWith({})

    def test_render_html_parent_context_when_other_variable_in_context(self):
        self.set_parent_template("{% component my_component %}")

        self.render_parent_template_with_context(
            {
                "my_component": self.component,
                "test": "something",
            }
        )

        self.assertRenderHTMLCalledWith({"test": "something"})

    def test_render_html_parent_context_when_with_block_sets_extra_context(self):
        self.set_parent_template(
            "{% with test='something' %}{% component my_component %}{% endwith %}"
        )

        self.render_parent_template_with_context({"my_component": self.component})

        self.assertRenderHTMLCalledWith({"test": "something"})

    def test_render_html_parent_context_when_with_keyword_sets_extra_context(self):
        self.set_parent_template("{% component my_component with test='something' %}")

        self.render_parent_template_with_context({"my_component": self.component})

        self.assertRenderHTMLCalledWith({"test": "something"})

    def test_render_html_parent_context_when_with_only_keyword_limits_extra_context(
        self,
    ):
        self.set_parent_template(
            "{% component my_component with test='nothing else' only %}"
        )

        self.render_parent_template_with_context(
            {
                "my_component": self.component,
                "other": "something else",
            }
        )

        # The `other` variable from the parent's rendering context is not included in
        # the context that is passed to the `render_html` method. This is because of the
        # `only` keyword.
        self.assertRenderHTMLCalledWith({"test": "nothing else"})

    def test_render_html_parent_context_when_with_block_overrides_context(self):
        self.set_parent_template(
            "{% with test='something else' %}{% component my_component %}{% endwith %}"
        )

        self.render_parent_template_with_context(
            {
                "my_component": self.component,
                "test": "something",
            }
        )

        self.assertRenderHTMLCalledWith({"test": "something else"})

    def test_render_html_parent_context_when_with_keyword_overrides_context(self):
        self.set_parent_template(
            "{% component my_component with test='something else' %}"
        )

        self.render_parent_template_with_context(
            {
                "my_component": self.component,
                "test": "something",
            }
        )

        self.assertRenderHTMLCalledWith({"test": "something else"})

    def test_render_html_parent_context_when_with_keyword_overrides_with_block(self):
        self.set_parent_template(
            """
            {% with test='something' %}
            {% component my_component with test='something else' %}
            {% endwith %}
            """
        )

        self.render_parent_template_with_context({"my_component": self.component})

        self.assertRenderHTMLCalledWith({"test": "something else"})

    def test_fallback_render_method_arg_true_and_object_with_render_method(self):
        # -----------------------------------------------------------------------------
        class ExampleNonComponentWithRenderMethod:
            def render(self):
                return "Rendered non-component"

        # -----------------------------------------------------------------------------
        non_component = ExampleNonComponentWithRenderMethod()
        self.set_parent_template(
            "{% component my_non_component fallback_render_method=True %}"
        )

        result = self.render_parent_template_with_context(
            {"my_non_component": non_component},
        )

        self.assertEqual(result, "Rendered non-component")

    def test_fallback_render_method_arg_true_but_object_without_render_method(self):
        # -----------------------------------------------------------------------------
        class ExampleNonComponentWithoutRenderMethod:
            pass

        # -----------------------------------------------------------------------------
        non_component = ExampleNonComponentWithoutRenderMethod()
        self.set_parent_template(
            "{% component my_non_component fallback_render_method=True %}"
        )

        with self.assertRaises(ValueError):
            self.render_parent_template_with_context(
                {"my_non_component": non_component},
            )

    def test_no_fallback_render_method_arg_and_object_without_render_method(self):
        # -----------------------------------------------------------------------------
        class ExampleNonComponentWithoutRenderMethod:
            pass

        # -----------------------------------------------------------------------------
        non_component = ExampleNonComponentWithoutRenderMethod()
        self.set_parent_template("{% component my_non_component %}")

        with self.assertRaises(ValueError):
            self.render_parent_template_with_context(
                {"my_non_component": non_component},
            )

    def test_render_html_return_in_parent_template_is_escaped(self):
        self.component.render_html.return_value = (
            "Look, I'm running with scissors! 8< 8< 8<"
        )
        self.set_parent_template("{% component my__component %}")

        result = self.render_parent_template_with_context(
            {"my__component": self.component},
        )

        self.assertEqual(
            result, "Look, I&#x27;m running with scissors! 8&lt; 8&lt; 8&lt;"
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

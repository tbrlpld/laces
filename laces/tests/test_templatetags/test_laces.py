import os
import random

from pathlib import Path
from unittest.mock import Mock

from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError
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
        self.component.render_html = Mock(return_value="Rendered HTML")

    def set_parent_template(self, template_string):
        template_string = "{% load laces %}" + template_string
        self.parent_template = Template(template_string)

    def render_parent_template_with_context(self, context: dict):
        return self.parent_template.render(Context(context))

    def assertRenderHTMLCalledWith(self, context: dict):
        self.component.render_html.assert_called_with(Context(context))

    def test_render_html_return_in_parent_template(self):
        self.assertEqual(self.component.render_html(), "Rendered HTML")
        self.set_parent_template("Before {% component my_component %} After")

        result = self.render_parent_template_with_context(
            {"my_component": self.component},
        )

        # This matches the return value of the `render_html` method inserted into the
        # parent template.
        self.assertEqual(result, "Before Rendered HTML After")

    def test_render_html_return_is_escaped(self):
        self.component.render_html.return_value = (
            "Look, I'm running with scissors! 8< 8< 8<"
        )
        self.set_parent_template("{% component my_component %}")

        result = self.render_parent_template_with_context(
            {"my_component": self.component},
        )

        self.assertEqual(
            result,
            "Look, I&#x27;m running with scissors! 8&lt; 8&lt; 8&lt;",
        )

    def test_render_html_return_not_escaped_when_formatted_html(self):
        self.component.render_html.return_value = format_html("<h1>My component</h1>")
        self.set_parent_template("{% component my_component %}")

        result = self.render_parent_template_with_context(
            {"my_component": self.component},
        )

        self.assertEqual(result, "<h1>My component</h1>")

    def test_render_html_return_not_escaped_when_actually_rendered_template(self):
        example_template_name = f"example-{random.randint(1000, 10000)}.html"
        example_template = (
            Path(settings.PROJECT_DIR) / "templates" / example_template_name
        )
        with open(example_template, "w") as f:
            f.write("<h1>My component</h1>")

        # -----------------------------------------------------------------------------
        class RealExampleComponent(Component):
            template_name = example_template_name

        # -----------------------------------------------------------------------------
        component = RealExampleComponent()
        self.set_parent_template("{% component my_component %}")

        result = self.render_parent_template_with_context(
            {"my_component": component},
        )

        self.assertEqual(result, "<h1>My component</h1>")
        os.remove(example_template)

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
        # the context that is passed to the `render_html` method. The `test` variable,
        # that was defined with the with-keyword, is present though. Both of these
        # effects come form the `only` keyword.
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
            def __repr__(self):
                return "<Example repr>"

        # -----------------------------------------------------------------------------
        non_component = ExampleNonComponentWithoutRenderMethod()
        self.set_parent_template("{% component my_non_component %}")

        with self.assertRaises(ValueError) as cm:
            self.render_parent_template_with_context(
                {"my_non_component": non_component},
            )
        self.assertEqual(
            str(cm.exception),
            "Cannot render <Example repr> as a component",
        )

    def test_as_keyword_stores_render_html_return_as_variable(self):
        self.set_parent_template(
            "{% component my_component as my_var %}The result was: {{ my_var }}"
        )

        result = self.render_parent_template_with_context(
            {"my_component": self.component},
        )

        self.assertEqual(result, "The result was: Rendered HTML")

    def test_as_keyword_without_variable_name(self):
        # The template is already parsed when the parent template is set. This is the
        # moment where the parsing error is raised.
        with self.assertRaises(TemplateSyntaxError) as cm:
            self.set_parent_template("{% component my_component as %}")

        self.assertEqual(
            str(cm.exception),
            "'component' tag with 'as' must be followed by a variable name",
        )

    def test_autoescape_off_block_can_disable_escaping_of_render_html_return(self):
        self.component.render_html.return_value = (
            "Look, I'm running with scissors! 8< 8< 8<"
        )
        self.set_parent_template(
            "{% autoescape off %}{% component my_component %}{% endautoescape %}"
        )

        result = self.render_parent_template_with_context(
            {"my_component": self.component},
        )

        self.assertEqual(
            result,
            "Look, I'm running with scissors! 8< 8< 8<",
        )

    def test_parsing_no_arguments(self):
        # The template is already parsed when the parent template is set. This is the
        # moment where the parsing error is raised.
        with self.assertRaises(TemplateSyntaxError) as cm:
            self.set_parent_template("{% component %}")

        self.assertEqual(
            str(cm.exception),
            "'component' tag requires at least one argument, the component object",
        )

    def test_parsing_unknown_kwarg(self):
        # The template is already parsed when the parent template is set. This is the
        # moment where the parsing error is raised.
        with self.assertRaises(TemplateSyntaxError) as cm:
            self.set_parent_template("{% component my_component unknown_kwarg=True %}")

        self.assertEqual(
            str(cm.exception),
            "'component' tag only accepts 'fallback_render_method' as a keyword argument",
        )

    def test_parsing_unknown_bit(self):
        # The template is already parsed when the parent template is set. This is the
        # moment where the parsing error is raised.
        with self.assertRaises(TemplateSyntaxError) as cm:
            self.set_parent_template("{% component my_component unknown_bit %}")

        self.assertEqual(
            str(cm.exception),
            "'component' tag received an unknown argument: 'unknown_bit'",
        )

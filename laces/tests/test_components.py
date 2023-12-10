import os
import random

from pathlib import Path

from django.conf import settings
from django.forms.widgets import Media
from django.template import Context
from django.test import SimpleTestCase
from django.utils.html import SafeString

from laces.components import Component


class TestComponent(SimpleTestCase):
    """Directly test the Component class."""

    def setUp(self):
        self.component = Component()

    def test_render_html(self):
        """Test the `render_html` method."""
        # The default Component does not specify a `tempalte_name` attribute which is
        # required for `render_html`.
        with self.assertRaises(AttributeError):
            self.component.render_html()

    def test_get_context_data_parent_context_empty_context(self):
        """
        Test the default get_context_data.

        The parent context should not matter, but we use it as it is used in
        `render_html`.
        """
        result = self.component.get_context_data(parent_context=Context())

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_media(self):
        """
        Test the `media` property.

        The `media` property is added through the `metaclass=MediaDefiningClass`
        definition.

        """
        self.assertIsInstance(self.component.media, Media)
        empty_media = Media()
        self.assertEqual(self.component.media._css, empty_media._css)
        self.assertEqual(self.component.media._js, empty_media._js)


class TestComponentSubclasses(SimpleTestCase):
    """
    Test the Component class through  subclasses.

    Most functionality of the Component class is only unlocked through subclassing and
    definition of certain attributes (like `template_name`) or overriding of the
    existing methods.
    """

    @classmethod
    def make_example_template_name(cls):
        return f"example-{random.randint(1000, 10000)}.html"

    @classmethod
    def get_example_template_name(cls):
        example_template_name = cls.make_example_template_name()
        while os.path.exists(example_template_name):
            example_template_name = cls.make_example_template_name()
        return example_template_name

    def setUp(self):
        self.example_template_name = self.get_example_template_name()
        self.example_template = (
            Path(settings.PROJECT_DIR) / "templates" / self.example_template_name
        )

    def set_example_template_content(self, content: str):
        with open(self.example_template, "w") as f:
            f.write(content)

    def test_render_html_with_template_name_set(self):
        # -----------------------------------------------------------------------------
        class ExampleComponent(Component):
            template_name = self.example_template_name

        # -----------------------------------------------------------------------------

        self.set_example_template_content("Test")

        result = ExampleComponent().render_html()

        self.assertIsInstance(result, str)
        self.assertIsInstance(result, SafeString)
        self.assertEqual(result, "Test")

    def test_render_html_with_template_name_set_and_data_from_get_context_data(self):
        # -----------------------------------------------------------------------------
        class ExampleComponent(Component):
            template_name = self.example_template_name

            def get_context_data(self, parent_context):
                return {"name": "World"}

        # -----------------------------------------------------------------------------

        self.set_example_template_content("Hello {{ name }}")

        result = ExampleComponent().render_html()

        self.assertEqual(result, "Hello World")

    def tearDown(self):
        os.remove(path=self.example_template)

import os
import random

from pathlib import Path

from django.conf import settings
from django.forms.widgets import Media
from django.template import Context
from django.test import SimpleTestCase
from django.utils.html import SafeString

from laces.components import Component, MediaContainer


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
        # We need to compare the internal dicts and lists as the `Media` class does not
        # implement `__eq__`.
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
        # Write content to the template file to ensure it exists.
        self.set_example_template_content("")

    def set_example_template_content(self, content: str):
        with open(self.example_template, "w") as f:
            f.write(content)

    def test_render_html_with_template_name_set(self):
        """
        Test the `render_html` with a set `template_name` attribute.
        """

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
        """
        Test the `render_html` with `get_context_data` providing data for the context.
        """

        # -----------------------------------------------------------------------------
        class ExampleComponent(Component):
            template_name = self.example_template_name

            def get_context_data(self, parent_context):
                return {"name": "World"}

        # -----------------------------------------------------------------------------

        self.set_example_template_content("Hello {{ name }}")

        result = ExampleComponent().render_html()

        self.assertEqual(result, "Hello World")

    def test_render_html_when_get_context_data_returns_None(self):
        """
        Test the `render_html` method when `get_context_data` returns `None`.

        This behavior was present when the class was extracted. It is not totally clear
        why this specific check is needed. By default, the `get_context_data` method
        provides and empty dict. If an override wanted to `get_context_data` return
        `None`, it should be expected that no context data is available during
        rendering. The underlying `template.render` method does not seem to care about
        `None` as the context.
        """

        # -----------------------------------------------------------------------------
        class ExampleComponent(Component):
            def get_context_data(self, parent_context):
                return None

        # -----------------------------------------------------------------------------

        with self.assertRaises(TypeError):
            ExampleComponent().render_html()

    def test_media_defined_through_nested_class(self):
        """
        Test the `media` property when defined through a nested class.

        The `media` property is added through the `metaclass=MediaDefiningClass`
        definition. This test ensures that the `media` property is available when
        configured through a nested class.
        """

        # -----------------------------------------------------------------------------
        class ExampleComponent(Component):
            class Media:
                css = {"all": ["example.css"]}
                js = ["example.js"]

        # -----------------------------------------------------------------------------

        result = ExampleComponent().media

        self.assertIsInstance(result, Media)
        self.assertEqual(result._css, {"all": ["example.css"]})
        self.assertEqual(result._js, ["example.js"])

    def tearDown(self):
        os.remove(path=self.example_template)


class TestMediaContainer(SimpleTestCase):
    """
    Test the MediaContainer class.

    The `MediaContainer` functionality depends on the `django.forms.widgets.Media`
    class. The `Media` class provides the logic to combine the media definitions of
    multiple objects through its `__add__` method. The `MediaContainer` relies on this
    functionality to provide a `media` property that combines the media definitions of
    its members.

    See also:
    https://docs.djangoproject.com/en/4.2/topics/forms/media
    """

    def setUp(self):
        self.media_container = MediaContainer()

    def test_empty(self):
        result = self.media_container.media

        self.assertIsInstance(result, Media)
        self.assertEqual(result._css, {})
        self.assertEqual(result._js, [])

    def test_single_member(self):
        # -----------------------------------------------------------------------------
        class ExampleClass:
            media = Media(css={"all": ["example.css"]})

        # -----------------------------------------------------------------------------
        example = ExampleClass()
        self.media_container.append(example)

        result = self.media_container.media

        self.assertIsInstance(result, Media)
        self.assertEqual(result._css, example.media._css)
        self.assertEqual(result._css, {"all": ["example.css"]})
        self.assertEqual(result._js, example.media._js)
        self.assertEqual(result._js, [])

    def test_two_members_of_same_class(self):
        # -----------------------------------------------------------------------------
        class ExampleClass:
            media = Media(css={"all": ["example.css"]}, js=["example.js"])

        # -----------------------------------------------------------------------------
        example = ExampleClass()
        self.media_container.append(example)

        result = self.media_container.media

        self.assertIsInstance(result, Media)
        self.assertEqual(result._css, example.media._css)
        self.assertEqual(result._css, {"all": ["example.css"]})
        self.assertEqual(result._js, example.media._js)
        self.assertEqual(result._js, ["example.js"])

    def test_two_members_of_different_classes(self):
        # -----------------------------------------------------------------------------
        class ExampleClass:
            media = Media(css={"all": ["shared.css"]}, js=["example.js"])

        class OtherExampleClass:
            media = Media(
                css={
                    "all": ["other.css", "shared.css"],
                    "print": ["print.css"],
                },
                js=["other.js"],
            )

        # -----------------------------------------------------------------------------
        example = ExampleClass()
        self.media_container.append(example)
        other = OtherExampleClass()
        self.media_container.append(other)

        result = self.media_container.media

        self.assertIsInstance(result, Media)
        self.assertEqual(
            result._css,
            {
                "all": ["other.css", "shared.css"],
                "print": ["print.css"],
            },
        )
        self.assertEqual(result._js, ["example.js", "other.js"])

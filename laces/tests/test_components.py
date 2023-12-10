from django.forms.widgets import Media
from django.template import Context
from django.test import SimpleTestCase

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

"""
Tests for a variety of different ways how components may be used.
"""
from django.test import SimpleTestCase

from laces.test.example.components import (
    PassesFixedNameToContextComponent,
    RendersTemplateWithFixedContentComponent,
    ReturnsFixedContentComponent,
)


class TestRendersTempalteWithFixedContentComponent(SimpleTestCase):
    """Test that the template is rendered."""

    def setUp(self):
        self.component = RendersTemplateWithFixedContentComponent()

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/hello-world.html",
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Hello World</h1>\n",
        )


class TestReturnsFixedContentComponent(SimpleTestCase):
    """Test the component that returns fixed content."""

    def setUp(self):
        self.component = ReturnsFixedContentComponent()

    def test_template_name(self):
        self.assertFalse(hasattr(self.component, "template_name"))

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Hello World Return</h1>\n",
        )


class TestPassesFixedNameToContextComponent(SimpleTestCase):
    """Test that the context is used to render the template."""

    def setUp(self):
        self.component = PassesFixedNameToContextComponent()

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/hello-name.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(),
            {"name": "Alice"},
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Hello Alice</h1>\n",
        )

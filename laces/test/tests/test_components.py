"""
Tests for the example components.

These tests are very basic and only ensure that the examples are configured as
desired. More thorough tests can be found in the `laces.tests.test_components` module.
"""
from django.test import SimpleTestCase

from laces.test.example.components import (
    DataclassAsDictContextComponent,
    HeadingComponent,
    ListSectionComponent,
    ParagraphComponent,
    PassesFixedNameToContextComponent,
    PassesInstanceAttributeToContextComponent,
    PassesNameFromParentContextComponent,
    PassesSelfToContextComponent,
    RendersTemplateWithFixedContentComponent,
    ReturnsFixedContentComponent,
    SectionWithHeadingAndParagraphComponent,
)


class TestRendersTemplateWithFixedContentComponent(SimpleTestCase):
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


class TestPassesInstanceAttributeToContextComponent(SimpleTestCase):
    def setUp(self):
        self.component = PassesInstanceAttributeToContextComponent(name="Bob")

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/hello-name.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(),
            {"name": "Bob"},
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Hello Bob</h1>\n",
        )


class TestPassesSelfToContextComponent(SimpleTestCase):
    def setUp(self):
        self.component = PassesSelfToContextComponent(name="Carol")

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/hello-self-name.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(),
            {"self": self.component},
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Hello Carol's self</h1>\n",
        )


class TestDataclassAsDictContextComponent(SimpleTestCase):
    def setUp(self):
        self.component = DataclassAsDictContextComponent(name="Charlie")

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/hello-name.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(),
            {"name": "Charlie"},
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Hello Charlie</h1>\n",
        )


class TestPassesNameFromParentContextComponent(SimpleTestCase):
    def setUp(self):
        self.component = PassesNameFromParentContextComponent()

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/hello-name.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(parent_context={"name": "Dan"}),
            {"name": "Dan"},
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(parent_context={"name": "Dan"}),
            "<h1>Hello Dan</h1>\n",
        )


class TestSectionWithHeadingAndParagraphComponent(SimpleTestCase):
    def setUp(self):
        self.heading = HeadingComponent(text="Heading")
        self.content = ParagraphComponent(text="Paragraph")
        self.component = SectionWithHeadingAndParagraphComponent(
            heading=self.heading,
            content=self.content,
        )

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/section.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(),
            {
                "heading": self.heading,
                "content": self.content,
            },
        )

    def test_render_html(self):
        self.assertHTMLEqual(
            self.component.render_html(),
            """
            <section>
                <h2>Heading</h2>
                <p>Paragraph</p>
            </section>
            """,
        )


class TestListSection(SimpleTestCase):
    def setUp(self):
        self.heading = HeadingComponent(text="Heading")
        self.item = ParagraphComponent(text="Paragraph")
        self.component = ListSectionComponent(
            heading=self.heading,
            items=[self.item],
        )

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/list-section.html",
        )

    def test_get_context_data(self):
        self.assertEqual(
            self.component.get_context_data(),
            {
                "heading": self.heading,
                "items": [self.item],
            },
        )

    def test_render_html(self):
        self.assertHTMLEqual(
            self.component.render_html(),
            """
            <section>
                <h2>Heading</h2>
                <ul>
                    <li>
                        <p>Paragraph</p>
                    </li>
                </ul>
            </section>
            """,
        )

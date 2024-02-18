"""Tests for the example views that demonstrate the use of components."""

from http import HTTPStatus

import django

from django.test import RequestFactory, TestCase

from laces.test.example.views import kitchen_sink


class TestKitchenSink(TestCase):
    def test_get(self) -> None:
        factory = RequestFactory()
        request = factory.get("/")

        response = kitchen_sink(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_html = response.content.decode("utf-8")
        self.assertInHTML("<h1>Hello World</h1>", response_html)
        self.assertInHTML("<h1>Hello World Return</h1>", response_html)
        self.assertInHTML("<h1>Hello Alice</h1>", response_html)
        self.assertInHTML("<h1>Hello Bob</h1>", response_html)
        self.assertInHTML("<h1>Hello Carol's self</h1>", response_html)
        self.assertInHTML("<h1>Hello Charlie</h1>", response_html)
        self.assertInHTML("<h1>Hello Dan</h1>", response_html)
        self.assertInHTML("<h1>Hello Erin Keyword</h1>", response_html)
        self.assertInHTML("<h1>Hello Erin Block</h1>", response_html)
        self.assertInHTML("<h1>Hello Erin Keyword over Block</h1>", response_html)
        self.assertInHTML(
            """
            <section>
                <h2>Hello</h2>
                <p>World</p>
            </section>
            """,
            response_html,
        )
        self.assertInHTML(
            """
            <section>
                <h2>Heading</h2>
                <ul>
                    <li>
                        <p>Item 1</p>
                    </li>
                    <li>
                        <blockquote>Item 2</blockquote>
                    </li>
                    <li>
                        <p>Item 3</p>
                    </li>
                </ul>
            </section>
            """,
            response_html,
        )
        self.assertInHTML("<h1>Hello Media</h1>", response_html)
        if django.VERSION < (4, 0):
            # Before Django 4.0 the markup was including the (useless)
            # `type="text/css"` attribute.
            self.assertInHTML(
                '<link href="/static/component.css" type="text/css" media="all" rel="stylesheet">',  # noqa: E501
                response_html,
            )
        else:
            self.assertInHTML(
                '<link href="/static/component.css" media="all" rel="stylesheet">',
                response_html,
            )
        self.assertInHTML('<script src="/static/component.js"></script>', response_html)
        self.assertInHTML("<header>Header with Media</header>", response_html)
        self.assertInHTML("<footer>Footer with Media</footer>", response_html)
        if django.VERSION < (4, 0):
            self.assertInHTML(
                '<link href="/static/header.css" type="text/css" media="all" rel="stylesheet">',  # noqa: E501
                response_html,
            )
            self.assertInHTML(
                '<link href="/static/footer.css" type="text/css" media="all" rel="stylesheet">',  # noqa: E501
                response_html,
            )
        else:
            self.assertInHTML(
                '<link href="/static/header.css" media="all" rel="stylesheet">',
                response_html,
            )
            self.assertInHTML(
                '<link href="/static/footer.css" media="all" rel="stylesheet">',
                response_html,
            )
        self.assertInHTML('<script src="/static/header.js"></script>', response_html)
        self.assertInHTML('<script src="/static/footer.js"></script>', response_html)
        self.assertInHTML(
            '<script src="/static/common.js"></script>',
            response_html,
            count=1,
        )


class TestServeComponent(TestCase):
    """
    Test the serve view from the perspective of an external project.

    The functionality is not defined in this project. It's in Laces, but I want to have
    some use cases of how this maybe be used.

    This makes some assumptions about what is set up in the project. There will need to
    be other more encapsulated tests in Laces directly.

    """

    def test_get_component(self) -> None:
        # Requesting the `laces.test.example.components.RendersTemplateWithFixedContentComponent`
        response = self.client.get("/components/renders-fixed-content-template/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertHTMLEqual(
            response.content.decode("utf-8"),
            "<h1>Hello World</h1>",
        )

"""Tests for the example views that demonstrate the use of components."""

from http import HTTPStatus

import django

from django import urls
from django.test import RequestFactory, TestCase

from laces.test.example.views import kitchen_sink


class TestKitchenSink(TestCase):
    def test_with_request(self) -> None:
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

    def test_get(self) -> None:
        url = urls.reverse("kitchen_sink")

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestSingleComponentView(TestCase):
    def test_get(self) -> None:
        url = urls.reverse("single_component")

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_html = response.content.decode("utf-8")
        self.assertHTMLEqual(response_html, "<h1>Hello World</h1>")
        self.assertIn("request", response.context)
        self.assertIn("user", response.context)


class TestComponentResponseView(TestCase):
    def test_get(self) -> None:
        url = urls.reverse("component_response")

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_html = response.content.decode("utf-8")
        self.assertHTMLEqual(response_html, "<h1>Hello World</h1>")
        # Testing that the context processors are run. This would happen if you
        # generated a response in the typical Django way with a top-level template.
        # (E.g. `django.shortcuts.render` or `django.template.response.TemplateResponse`)
        self.assertIn("request", response.context)
        self.assertIn("user", response.context)

    def test_get_compared_to_single_component_view(self) -> None:
        # Component response view
        component_url = urls.reverse("single_component")
        # component_url = urls.reverse("component_response")
        component_response = self.client.get(component_url)
        self.assertEqual(component_response.status_code, HTTPStatus.OK)

        # Single component view
        single_url = urls.reverse("single_component")
        single_response = self.client.get(single_url)
        self.assertEqual(single_response.status_code, HTTPStatus.OK)

        self.maxDiff = None

        # String representation
        self.assertEqual(str(component_response), str(single_response))

        # Content
        component_response_html = component_response.content.decode("utf-8")
        single_response_html = single_response.content.decode("utf-8")
        self.assertHTMLEqual(component_response_html, single_response_html)

        # Context
        self.assertEqual(
            # Cannot compare the contents because they include reprs with memory
            # addresses.
            component_response.context.keys(),
            single_response.context.keys(),
        )

        # Headers
        self.assertEqual(
            component_response.headers,
            single_response.headers,
        )

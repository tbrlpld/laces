"""Tests for the example views that demonstrate the use of components."""
from http import HTTPStatus

from django.test import RequestFactory, TestCase

from laces.test.example.views import kitchen_sink


class TestKitchenSink(TestCase):
    def test_get(self):
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
        self.assertInHTML("<h1>Hello Erin</h1>", response_html)
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
        self.assertInHTML(
            '<link href="/static/component.css" media="all" rel="stylesheet">',
            response_html,
        )
        self.assertInHTML('<script src="/static/component.js"></script>', response_html)

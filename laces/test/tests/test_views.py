from http import HTTPStatus

from django.test import RequestFactory, TestCase

from laces.test.example.views import kitchen_sink


class TestKitchenSink(TestCase):
    def test_get(self):
        factory = RequestFactory()
        request = factory.get("/")

        response = kitchen_sink(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "<h1>Hello World</h1>")
        self.assertContains(response, "<h1>Hello World Return</h1>")
        self.assertContains(response, "<h1>Hello Alice</h1>")
        self.assertContains(response, "<h1>Hello Bob</h1>")
        self.assertContains(response, "<h1>Hello Charlie</h1>")
        self.assertContains(response, "<h1>Hello Dan</h1>")
        self.assertContains(response, "<h1>Hello Erin</h1>")
        self.assertContains(response, "<h1>Hello Faythe</h1>")

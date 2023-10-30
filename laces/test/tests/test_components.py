from django import test

from laces.test import components as test_components


class TestComponents(test.TestCase):
    def test_component(self):
        component = test_components.TestComponent()

        self.assertEqual(component.render(), "Hello, world!")

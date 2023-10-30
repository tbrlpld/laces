from django import test

import laces

from laces.test import components as test_components


class TestComponent(test.TestCase):
    def test_inherits_laces_component(self):
        self.assertTrue(issubclass(test_components.TestComponent, laces.Component))

    def test_component(self):
        component = test_components.TestComponent()

        self.assertEqual(component.render(), "Hello, world!")

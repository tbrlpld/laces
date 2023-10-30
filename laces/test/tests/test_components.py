import typing

from django import test

import laces

from laces import components
from laces.test import components as test_components


class TestComponent(test.TestCase):
    def test_available(self):
        self.assertTrue(hasattr(components, "Component"))

    def test_available_on_package_level(self):
        self.assertEqual(
            components.Component,
            laces.Component,
        )

    def test_has_render_method(self):
        self.assertTrue(hasattr(components.Component, "render"))
        self.assertTrue(isinstance(components.Component.render, typing.Callable))


class TestStaticComponent(test.TestCase):
    def test_inherits_laces_component(self):
        self.assertTrue(issubclass(test_components.StaticComponent, laces.Component))

    def test_defined_template(self):
        self.assertEqual(
            test_components.StaticComponent.template,
            "test_components/static.html",
        )

    def test_render(self):
        component = test_components.StaticComponent()

        self.assertEqual(component.render(), "Hello, world!")

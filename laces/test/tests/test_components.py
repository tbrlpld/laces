from django.test import SimpleTestCase

from laces.test.components import StaticTemplate


class TestStaticTemplate(SimpleTestCase):
    def setUp(self):
        self.component = StaticTemplate()

    def test_template_name(self):
        self.assertEqual(
            self.component.template_name,
            "components/static-template.html",
        )

    def test_render_html(self):
        self.assertEqual(
            self.component.render_html(),
            "<h1>Static Template</h1>\n",
        )

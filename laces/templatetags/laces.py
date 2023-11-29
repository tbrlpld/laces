from django import template
from django.template.base import token_kwargs
from django.template.defaultfilters import conditional_escape


register = template.library.Library()


class ComponentNode(template.Node):
    """
    Template node to render a component.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/094834909d5c4b48517fd2703eb1f6d386572ffa/wagtail/admin/templatetags/wagtailadmin_tags.py#L937-L987  # noqa: E501
    """

    def __init__(
        self,
        component,
        extra_context=None,
        isolated_context=False,
        fallback_render_method=None,
        target_var=None,
    ):
        self.component = component
        self.extra_context = extra_context or {}
        self.isolated_context = isolated_context
        self.fallback_render_method = fallback_render_method
        self.target_var = target_var

    def render(self, context: template.Context) -> str:
        # Render a component by calling its render_html method, passing request and context from the
        # calling template.
        # If fallback_render_method is true, objects without a render_html method will have render()
        # called instead (with no arguments) - this is to provide deprecation path for things that have
        # been newly upgraded to use the component pattern.

        component = self.component.resolve(context)

        if self.fallback_render_method:
            fallback_render_method = self.fallback_render_method.resolve(context)
        else:
            fallback_render_method = False

        values = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }

        if hasattr(component, "render_html"):
            if self.isolated_context:
                html = component.render_html(context.new(values))
            else:
                with context.push(**values):
                    html = component.render_html(context)
        elif fallback_render_method and hasattr(component, "render"):
            html = component.render()
        else:
            raise ValueError(f"Cannot render {component!r} as a component")

        if self.target_var:
            context[self.target_var] = html
            return ""
        else:
            if context.autoescape:
                html = conditional_escape(html)
            return html


@register.tag(name="component")
def component(parser, token):
    """
    Template tag to render a component via ComponentNode.

    Extracted from Wagtail. See:
    https://github.com/wagtail/wagtail/blob/094834909d5c4b48517fd2703eb1f6d386572ffa/wagtail/admin/templatetags/wagtailadmin_tags.py#L990-L1037  # noqa: E501
    """
    bits = token.split_contents()[1:]
    if not bits:
        raise template.TemplateSyntaxError(
            "'component' tag requires at least one argument, the component object"
        )

    component = parser.compile_filter(bits.pop(0))

    # the only valid keyword argument immediately following the component
    # is fallback_render_method
    flags = token_kwargs(bits, parser)
    fallback_render_method = flags.pop("fallback_render_method", None)
    if flags:
        raise template.TemplateSyntaxError(
            "'component' tag only accepts 'fallback_render_method' as a keyword argument"
        )

    extra_context = {}
    isolated_context = False
    target_var = None

    while bits:
        bit = bits.pop(0)
        if bit == "with":
            extra_context = token_kwargs(bits, parser)
        elif bit == "only":
            isolated_context = True
        elif bit == "as":
            try:
                target_var = bits.pop(0)
            except IndexError:
                raise template.TemplateSyntaxError(
                    "'component' tag with 'as' must be followed by a variable name"
                )
        else:
            raise template.TemplateSyntaxError(
                "'component' tag received an unknown argument: %r" % bit
            )

    return ComponentNode(
        component,
        extra_context=extra_context,
        isolated_context=isolated_context,
        fallback_render_method=fallback_render_method,
        target_var=target_var,
    )

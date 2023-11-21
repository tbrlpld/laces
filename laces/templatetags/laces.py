from django.template import library


register = library.Library()


@register.simple_tag()
def component():
    pass

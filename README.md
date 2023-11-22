# Laces

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPI version](https://badge.fury.io/py/laces.svg)](https://badge.fury.io/py/laces)
[![laces CI](https://github.com/tbrlpld/laces/actions/workflows/test.yml/badge.svg)](https://github.com/tbrlpld/laces/actions/workflows/test.yml)

---

Django components that know how to render themselves.


Working with objects that know how to render themselves as HTML elements is a common pattern found in complex Django applications (e.g. the [Wagtail](https://github.com/wagtail/wagtail) admin interface).
This package provides tools enable and support working with such objects, also known as "components".

The APIs provided in the package have previously been discovered, developed and solidified in the Wagtail project.
The purpose of this package is to make these tools available to other Django projects outside the Wagtail ecosystem.


## Links

- [Documentation](https://github.com/tbrlpld/laces/blob/main/README.md)
- [Changelog](https://github.com/tbrlpld/laces/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/tbrlpld/laces/blob/main/CONTRIBUTING.md)
- [Discussions](https://github.com/tbrlpld/laces/discussions)
- [Security](https://github.com/tbrlpld/laces/security)

## Supported versions

- Python >= 3.8
- Django >= 3.2

## Installation

First, install with pip:
```sh
$ python -m pip install laces
```

Then, add to your installed apps:

```python
# settings.py

INSTALLED_APPS = ["laces", ...]
```

That's it.

## Usage


Working with objects that know how to render themselves as elements on an HTML template is a common pattern seen throughout the Wagtail admin. For example, the admin homepage is a view provided by the central `wagtail.admin` app, but brings together information panels sourced from various other modules of Wagtail, such as images and documents (potentially along with others provided by third-party packages). These panels are passed to the homepage via the [`construct_homepage_panels`](construct_homepage_panels) hook, and each one is responsible for providing its own HTML rendering. In this way, the module providing the panel has full control over how it appears on the homepage.

Wagtail implements this pattern using a standard object type known as a **component**. A component is a Python object that provides the following methods and properties:

```{eval-rst}
.. method:: render_html(self, parent_context=None)

Given a context dictionary from the calling template (which may be a :py:class:`Context <django.template.Context>` object or a plain ``dict`` of context variables), returns the string representation to be inserted into the template. This will be subject to Django's HTML escaping rules, so a return value consisting of HTML should typically be returned as a :py:mod:`SafeString <django.utils.safestring>` instance.

.. attribute:: media

A (possibly empty) :doc:`form media <django:topics/forms/media>` object defining JavaScript and CSS resources used by the component.
```

```{note}
   Any object implementing this API can be considered a valid component; it does not necessarily have to inherit from the `Component` class described below, and user code that works with components should not assume this (for example, it must not use `isinstance` to check whether a given value is a component).
```

(creating_template_components)=

### Creating components

The preferred way to create a component is to define a subclass of `wagtail.admin.ui.components.Component` and specify a `template_name` attribute on it. The rendered template will then be used as the component's HTML representation:

```python
from wagtail.admin.ui.components import Component


class WelcomePanel(Component):
    template_name = "my_app/panels/welcome.html"


my_welcome_panel = WelcomePanel()
```

`my_app/templates/my_app/panels/welcome.html`:

```html+django
<h1>Welcome to my app!</h1>
```

For simple cases that don't require a template, the `render_html` method can be overridden instead:

```python
from django.utils.html import format_html
from wagtail.admin.components import Component


class WelcomePanel(Component):
    def render_html(self, parent_context):
        return format_html("<h1>{}</h1>", "Welcome to my app!")
```

### Passing context to the template

The `get_context_data` method can be overridden to pass context variables to the template. As with `render_html`, this receives the context dictionary from the calling template:

```python
from wagtail.admin.ui.components import Component


class WelcomePanel(Component):
    template_name = "my_app/panels/welcome.html"

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        context["username"] = parent_context["request"].user.username
        return context
```

`my_app/templates/my_app/panels/welcome.html`:

```html+django
<h1>Welcome to my app, {{ username }}!</h1>
```

### Adding media definitions

Like Django form widgets, components can specify associated JavaScript and CSS resources using either an inner `Media` class or a dynamic `media` property:

```python
class WelcomePanel(Component):
    template_name = "my_app/panels/welcome.html"

    class Media:
        css = {"all": ("my_app/css/welcome-panel.css",)}
```

### Using components on your own templates

The `wagtailadmin_tags` tag library provides a `{% component %}` tag for including components on a template. This takes care of passing context variables from the calling template to the component (which would not be the case for a basic `{{ ... }}` variable tag). For example, given the view:

```python
from django.shortcuts import render


def welcome_page(request):
    panels = [
        WelcomePanel(),
    ]

    render(
        request,
        "my_app/welcome.html",
        {
            "panels": panels,
        },
    )
```

the `my_app/welcome.html` template could render the panels as follows:

```html+django
{% load wagtailadmin_tags %}
{% for panel in panels %}
    {% component panel %}
{% endfor %}
```

You can pass additional context variables to the component using the keyword `with`:

```html+django
{% component panel with username=request.user.username %}
```

To render the component with only the variables provided (and no others from the calling template's context), use `only`:

```html+django
{% component panel with username=request.user.username only %}
```

To store the component's rendered output in a variable rather than outputting it immediately, use `as` followed by the variable name:

```html+django
{% component panel as panel_html %}

{{ panel_html }}
```

Note that it is your template's responsibility to output any media declarations defined on the components. For a Wagtail admin view, this is best done by constructing a media object for the whole page within the view, passing this to the template, and outputting it via the base template's `extra_js` and `extra_css` blocks:

```python
from django.forms import Media
from django.shortcuts import render


def welcome_page(request):
    panels = [
        WelcomePanel(),
    ]

    media = Media()
    for panel in panels:
        media += panel.media

    render(
        request,
        "my_app/welcome.html",
        {
            "panels": panels,
            "media": media,
        },
    )
```

`my_app/welcome.html`:

```html+django
{% extends "wagtailadmin/base.html" %}
{% load wagtailadmin_tags %}

{% block extra_js %}
    {{ block.super }}
    {{ media.js }}
{% endblock %}

{% block extra_css %}
    {{ block.super }}
    {{ media.css }}
{% endblock %}

{% block content %}
    {% for panel in panels %}
        {% component panel %}
    {% endfor %}
{% endblock %}
```

## Contributing

### Install

To make changes to this project, first clone this repository:

```sh
$ git clone https://github.com/tbrlpld/laces.git
$ cd laces
```

With your preferred virtualenv activated, install testing dependencies:

#### Using pip

```sh
$ python -m pip install --upgrade pip>=21.3
$ python -m pip install -e '.[testing]' -U
```

#### Using flit

```sh
$ python -m pip install flit
$ flit install
```

### pre-commit

Note that this project uses [pre-commit](https://github.com/pre-commit/pre-commit).
It is included in the project testing requirements. To set up locally:

```shell
# go to the project directory
$ cd laces
# initialize pre-commit
$ pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
$ git ls-files --others --cached --exclude-standard | xargs pre-commit run --files
```

### How to run tests

Now you can run all tests like so:

```sh
$ tox
```

Or, you can run them for a specific environment:

```sh
$ tox -e python3.11-django4.2-wagtail5.1
```

Or, run only a specific test:

```sh
$ tox -e python3.11-django4.2-wagtail5.1-sqlite laces.tests.test_file.TestClass.test_method
```

To run the test app interactively, use:

```sh
$ tox -e interactive
```

You can now visit `http://localhost:8020/`.

### Python version management

Tox will attempt to find installed Python versions on your machine.
If you use `pyenv` to manage multiple versions, you can tell `tox` to use those versions.
This working, is depended on [`virtualenv-pyenv`](https://pypi.org/project/virtualenv-pyenv/) (note: this is not `pyenv-virtualenv`) which is part of the CI dependencies (just like `tox` itself is).
To enable the use, you want to set the environment variable `VIRTUALENV_DISCOVERY=pyenv`.

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

### Creating components

The preferred way to create a component is to define a subclass of `laces.components.Component` and specify a `template_name` attribute on it.
The rendered template will then be used as the component's HTML representation:

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/panels/welcome.html"


my_welcome_panel = WelcomePanel()
```

```html+django
{# my_app/templates/my_app/panels/welcome.html #}

<h1>Welcome to my app!</h1>
```

For simple cases that don't require a template, the `render_html` method can be overridden instead:

```python
# my_app/components.py

from django.utils.html import format_html
from laces.components import Component


class WelcomePanel(Component):
    def render_html(self, parent_context):
        return format_html("<h1>{}</h1>", "Welcome to my app!")
```

### Passing context to the template

The `get_context_data` method can be overridden to pass context variables to the template.
As with `render_html`, this receives the context dictionary from the calling template.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/panels/welcome.html"

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        context["username"] = parent_context["request"].user.username
        return context
```

```html+django
{# my_app/templates/my_app/panels/welcome.html #}

<h1>Welcome to my app, {{ username }}!</h1>
```

### Adding media definitions

Like Django form widgets, components can specify associated JavaScript and CSS resources using either an inner `Media` class or a dynamic `media` property.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/panels/welcome.html"

    class Media:
        css = {"all": ("my_app/css/welcome-panel.css",)}
```

### Using components in other templates

The `laces` tag library provides a `{% component %}` tag for including components on a template.
This takes care of passing context variables from the calling template to the component (which would not be the case for a basic `{{ ... }}` variable tag).

For example, given the view passes an instance of `WelcomePanel` to the context of `my_app/welcome.html`.

```python
# my_app/views.py

from django.shortcuts import render

from my_app.components import WelcomePanel


def welcome_page(request):
    panel = (WelcomePanel(),)

    return render(
        request,
        "my_app/welcome.html",
        {
            "panel": panel,
        },
    )
```

The template `my_app/templates/my_app/welcome.html` could render the panel as follows:

```html+django
{# my_app/templates/my_app/welcome.html #}

{% load laces %}
{% component panel %}
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

Note that it is your template's responsibility to output any media declarations defined on the components.
This can be done by constructing a media object for the whole page within the view, passing this to the template, and outputting it via `media.js` and `media.css`.

```python
# my_app/views.py

from django.forms import Media
from django.shortcuts import render

from my_app.components import WelcomePanel


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


```html+django
{# my_app/templates/my_app/welcome.html #}

{% load laces %}

<head>
    {{ media.js }}
    {{ media.css }}
<head>
<body>
    {% for panel in panels %}
        {% component panel %}
    {% endfor %}
</body>
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

### Publishing

This project uses the [Trusted Publisher model for PyPI releases](https://docs.pypi.org/trusted-publishers/).
This means that publishing is done through GitHub Actions when a [new release is created on GitHub](https://github.com/tbrlpld/laces/releases/new).

Before publishing a new release, make sure to update the changelog in `CHANGELOG.md` and the version number in `laces/__init__.py`.

To manually test publishing the package, you can use `flit`.
Be sure to configure the `testpypi` repository in your `~/.pypirc` file according to the Flit [documentation](https://flit.pypa.io/en/stable/upload.html#controlling-package-uploads).
If your PyPI account is using 2FA, you'll need to create a [PyPI API token](https://test.pypi.org/help/#apitoken) and use that as your password and `__token__` as the username.

When you're ready to test the publishing, run:

```shell
$ flit build
$ flit publish --repository testpypi
```

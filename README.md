# Laces

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPI version](https://badge.fury.io/py/laces.svg)](https://badge.fury.io/py/laces)
[![laces CI](https://github.com/tbrlpld/laces/actions/workflows/test.yml/badge.svg)](https://github.com/tbrlpld/laces/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tbrlpld/laces/graph/badge.svg?token=FMHEHNVPSX)](https://codecov.io/gh/tbrlpld/laces)

---

Django components that know how to render themselves.

Laces components provide a simple way to combine data (in the form of Python objects) with the Django templates that are meant to render that data.
The benefit of this combination is that the components can be used in other templates without having to worry about passing the right context variables to the template.
Template and data are tied together 😅 and they can be passed around together.
This becomes especially useful when components are nested — it allows us to avoid building the same nested structure twice (once in the data and again in the templates).

Working with objects that know how to render themselves as HTML elements is a common pattern found in complex Django applications, such as the [Wagtail](https://github.com/wagtail/wagtail) admin interface.
The Wagtail admin is also where the APIs provided in this package have previously been discovered, developed and solidified.
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

## Getting started

### Installation

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

### Creating components

The simplest way to create a component is to define a subclass of `laces.components.Component` and specify a `template_name` attribute on it.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"
```

```html+django
{# my_app/templates/my_app/components/welcome.html #}

<h1>Hello World!</h1>
```

With the above in place, you then instantiate the component (e.g. in a view) and pass it to another template for rendering.

```python
# my_app/views.py

from django.shortcuts import render

from my_app.components import WelcomePanel


def home(request):
    welcome = WelcomePanel()  # <-- Instantiates the component
    return render(
        request,
        "my_app/home.html",
        {"welcome": welcome},  # <-- Passes the component to the view template
    )
```

In the view template, we `load` the `laces` tag library and use the `{% component %}` tag to render the component.

```html+django
{# my_app/templates/my_app/home.html #}

{% load laces %}
{% component welcome %}  {# <-- Renders the component #}
```

That's it!
The component's template will be rendered right there in the view template.

Of course, this is a very simple example and not much more useful than using a simple `include`.
We will go into some more useful use cases below.

### Without a template

Before we dig deeper into the component use cases, just a quick note that components don't have to have a template.
For simple cases that don't require a template, the `render_html` method can be overridden instead.
If the return value contains HTML, it should be marked as safe using `django.utils.html.format_html` or `django.utils.safestring.mark_safe`.

```python
# my_app/components.py

from django.utils.html import format_html
from laces.components import Component


class WelcomePanel(Component):
    def render_html(self, parent_context):
        return format_html("<h1>Hello World!</h1>")
```

### Passing context to the component template

Now back to components with templates.

The example shown above with the static welcome message in the template is, of course, not very useful.
It seems more like an overcomplicated way to replace a simple `include`.

But, we rarely ever want to render templates with static content.
Usually, we want to pass some context variables to the template to be rendered.
This is where components start to become interesting.

The default implementation of `render_html` calls the component's `get_context_data` method to get the context variables to pass to the template.
The default implementation of `get_context_data` returns an empty dictionary.
To customize the context variables passed to the template, we can override `get_context_data`.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    def get_context_data(self, parent_context):
        return {"name": "Alice"}
```

```html+django
{# my_app/templates/my_app/components/welcome.html #}

<h1>Hello {{ name }}</h1>
```

With the above we are now rendering a welcome message with the name coming from the component's `get_context_data` method.
Nice.
But, still not very useful, as the name is still hardcoded — in the component method instead of the template, but hardcoded nonetheless.

#### Using class properties

When considering how to make the context of our components more useful, it's helpful to remember that components are just normal Python classes and objects.
So, you are basically free to get the context data into the component in any way you like.

For example, we can pass arguments to the constructor and use them in the component's methods, like `get_context_data`.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    def __init__(self, name):
        self.name = name

    def get_context_data(self, parent_context):
        return {"name": self.name}
```

Nice, this is getting better.
Now we can pass the name to the component when we instantiate it and pass the component ready to be rendered to the view template.

```python
# my_app/views.py

from django.shortcuts import render

from my_app.components import WelcomePanel


def home(request):
    welcome = WelcomePanel(name="Alice")
    return render(
        request,
        "my_app/home.html",
        {"welcome": welcome},
    )
```

So, as mentioned before, we can use the full power of Python classes and objects to provide context data to our components.
A couple more examples of how components can be used can be found [below](#patterns-for-using-components).

#### Using the parent context

You may have noticed in the above examples that the `render_html` and `get_context_data` methods take a `parent_context` argument.
This is the context of the template that is calling the component.
The `parent_context` is passed into the `render_html` method by the `{% component %}` template tag.
In the default implementation of the `render_html` method, the `parent_context` is then passed to the `get_context_data` method.
The default implementation of the `get_context_data` method, however, ignores the `parent_context` argument and returns an empty dictionary.
To make use of it, you will have to override the `get_context_data` method.

Relying on data from the parent context somewhat forgoes some of the benefits of components, which is tying the data and template together.
Especially for nested uses of components, you now require that the data in the right format is passed through all layers of templates again.
It is usually cleaner to provide all the data needed by the component directly to the component itself.

However, there may be cases where this is not possible or desirable.
For those cases, you have access to the parent context in the component's `get_context_data` method.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    def get_context_data(self, parent_context):
        return {"name": parent_context["request"].user.first_name}
```

(Of course, this could have also been achieved by passing the request or user object to the component in the view, but this is just an example.)

### Using components in other templates

It's already been mentioned in the [first example](#creating-components), that components are rendered in other templates using the `{% component %}` tag from the `laces` tag library.

Here is that example from above again, in which the view passes an instance of `WelcomePanel` to the context of `my_app/home.html`.

```python
# my_app/views.py

from django.shortcuts import render

from my_app.components import WelcomePanel


def home(request):
    welcome = WelcomePanel()

    return render(
        request,
        "my_app/home.html",
        {
            "welcome": welcome,
        },
    )
```

Then, in the `my_app/templates/my_app/home.html` template we render the welcome panel component as follows:

```html+django
{# my_app/templates/my_app/home.html #}

{% load laces %}
{% component welcome %}
```

This is the basic usage of components and should cover most cases.

However, the `{% component %}` tag also supports some additional features.
Specifically, the keywords `with`, `only` and `as` are supported, similar to how they work with the [`{% include %}`](https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#std-templatetag-include) tag.

#### Provide additional parent context variables with `with`

You can pass additional parent context variables to the component using the keyword `with`:

```html+django
{% component welcome with name=request.user.first_name %}
```

**Note**: These extra variables will be added to the `parent_context` which is passed to the component's `render_html` and `get_context_data` methods.
The default implementation of `get_context_data` ignores the `parent_context` argument, so you will have to override it to make use of the extra variables.
For more information see the above section on the [parent context](#using-the-parent-context).

#### Limit the parent context variables with `only`

To limit the parent context variables passed to the component to only those variables provided by the `with` keyword (and no others from the calling template's context), use `only`:

```html+django
{% component welcome with name=request.user.first_name only %}
```

**Note**: Both, `with` and `only`, only affect the `parent_context` which is passed to the component's `render_html` and `get_context_data` methods. They do not have any direct effect on actual context that is passed to the component's template. E.g. if the component's `get_context_data` method returns a dictionary which always contains a key `foo`, then that key will be available in the component's template, regardless of whether `only` was used or not.

#### Store the rendered output in a variable with `as`

To store the component's rendered output in a variable rather than outputting it immediately, use `as` followed by the variable name:

```html+django
{% component welcome as welcome_html %}

{{ welcome_html }}
```

### Adding JavaScript and CSS assets to a component

Like Django form widgets, components can specify associated JavaScript and CSS assets.
The assets for a component can be specified in the same way that [Django form assets are defined](https://docs.djangoproject.com/en/5.0/topics/forms/media).
This can be achieved using either an inner `Media` class or a dynamic `media` property.

An inner `Media` class definition looks like this:

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    class Media:
        css = {"all": ("my_app/css/welcome-panel.css",)}
```

The more dynamic definition via a `media` property looks like this:

```python
# my_app/components.py

from django.forms import Media

from laces.components import Component


class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    @property
    def media(self):
        return Media(css={"all": ("my_app/css/welcome-panel.css",)})
```

**Note**:
It is your template's responsibility to output any media declarations defined on the components.

In the example home template from above, we can output the component's media declarations like so:

```html+django
{# my_app/templates/my_app/home.html #}

{% load laces %}

<head>
    {{ welcome.media }}
<head>
<body>
    {% component welcome %}
</body>
```

TODO: Fix this section.
If you have many components, you can combine their media definitions into a single object with the `MediaContainer` class.
~~This can be done by constructing a media object for the whole page within the view, passing this to the template, and outputting it via `media.js` and `media.css`.~~

## Patterns for using components

### Using dataclasses

The above example is neat already, but is may become a little verbose when we have more than one or two arguments to pass to the component.
You would have to list them all manually in the constructor and then assign them to the context.

To make this a little easier, we can use dataclasses.

```python
# my_app/components.py

from dataclasses import dataclass, asdict

from laces.components import Component


@dataclass
class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    name: str

    def get_context_data(self, parent_context):
        return asdict(self)
```

With dataclasses we define the name and type of the properties we want to pass to the component in the class definition.
Then, we can use the `asdict` function to convert the dataclass instance to a dictionary that can be passed to the template context.
The `asdict` function only  contains the properties defined in the dataclass, so we don't have to worry about accidentally passing other properties to the template.

### Special constructor methods

### Nesting components

### Sets of components

## About Laces and Components

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
$ python -m pip install -e '.[dev]' -U
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

#### Testing with coverage

`tox` is configured to run tests with coverage.
The coverage report is combined for all environments.
This is done by using the `--append` flag when running coverage in `tox`.
This means it will also include previous results.

You can see the coverage report by running:

```sh
$ coverage report
```

To get a clean report, you can run `coverage erase` before running `tox`.

#### Running tests without tox

If you want to run tests without `tox`, you can use the `testmanage.py` script.
This script is a wrapper around Django's `manage.py` and will run tests with the correct settings.

To make this work, you need to have the `testing` dependencies installed.

```sh
$ python -m pip install -e '.[testing]' -U
```

Then you can run tests with:

```sh
$ ./testmanage.py test
````

To run tests with coverage, use:

```sh
$ coverage run ./testmanage.py test
```

### Python version management

Tox will attempt to find installed Python versions on your machine.
If you use `pyenv` to manage multiple versions, you can tell `tox` to use those versions.
This working, is depended on [`virtualenv-pyenv`](https://pypi.org/project/virtualenv-pyenv/) (note: this is not `pyenv-virtualenv`) which is part of the CI dependencies (just like `tox` itself is).
To enable the use, you want to set the environment variable `VIRTUALENV_DISCOVERY=pyenv`.

### Publishing

This project uses the [Trusted Publisher model for PyPI releases](https://docs.pypi.org/trusted-publishers/).
This means that publishing is done through GitHub Actions when a [new release is created on GitHub](https://github.com/tbrlpld/laces/releases/new).

To create a release you need a Git tag.
The tag can either be created on the command line and pushed or in the "create release" interface on GitHub.
The tag name should be the version number prefixed with a `v` (e.g. `v0.1.0`).

Before publishing a new release, make sure to update the changelog in `CHANGELOG.md` and the version number in `laces/__init__.py`.

To manually test publishing the package, you can use `flit`.
Be sure to configure the `testpypi` repository in your `~/.pypirc` file according to the Flit [documentation](https://flit.pypa.io/en/stable/upload.html#controlling-package-uploads).
If your PyPI account is using 2FA, you'll need to create a [PyPI API token](https://test.pypi.org/help/#apitoken) and use that as your password and `__token__` as the username.

When you're ready to test the publishing, run:

```shell
$ flit build
$ flit publish --repository testpypi
```

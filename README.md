# Laces

[![License: BSD-3-Clause](https://img.shields.io/github/license/tbrlpld/laces)](https://github.com/tbrlpld/laces/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/laces)](https://pypi.org/project/laces/)
[![laces CI](https://github.com/tbrlpld/laces/actions/workflows/test.yml/badge.svg)](https://github.com/tbrlpld/laces/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tbrlpld/laces/graph/badge.svg?token=FMHEHNVPSX)](https://codecov.io/gh/tbrlpld/laces)

---

Django components that know how to render themselves.

Laces components provide a simple way to combine data (in the form of Python objects) with the Django templates that are meant to render that data.
The components can then be simply rendered in any other template using the `{% component %}` template tag.
That parent template does not need to know anything about the component's template or data.
No need to receive, filter, restructure or pass any data to the component's template.
Just let the component render itself.

Template and data are tied together (sorry, not sorry 😅) in the component, and they can be passed around together.
This becomes especially useful when components are nested — it allows us to avoid building the same nested structure twice (once in the data and again in the templates).

Working with objects that know how to render themselves as HTML elements is a common pattern found in complex Django applications, such as the [Wagtail](https://github.com/wagtail/wagtail) admin interface.
The Wagtail admin is also where the APIs provided in this package have previously been discovered, developed and solidified.
The purpose of this package is to make these tools available to other Django projects outside the Wagtail ecosystem.

## Links

- [Getting started](#getting-started)
    - [Installation](#installation)
    - [Creating components](#creating-components)
    - [Passing context to the component template](#passing-context-to-the-component-template)
    - [Using components in other templates](#using-components-in-other-templates)
    - [Adding JavaScript and CSS assets to a component](#adding-javascript-and-css-assets-to-a-component)
- [Patterns for using components](#patterns-for-using-components)
  - [Nesting components](#nesting-components)
  - [Nested groups of components](#nested-groups-of-components)
  - [Container components](#container-components)
  - [Using dataclasses](#using-dataclasses)
- [About Laces and components](#about-laces-and-components)
- [Contributing](#contributing)
- [Changelog](https://github.com/tbrlpld/laces/blob/main/CHANGELOG.md)
- [Discussions](https://github.com/tbrlpld/laces/discussions)
- [Security](https://github.com/tbrlpld/laces/security)

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

With the above in place, you then instantiate the component (e.g., in a view) and pass it to another template for rendering.

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

As mentioned in the [first example](#creating-components), components are rendered in other templates using the `{% component %}` tag from the `laces` tag library.

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

#### Outputting component media in templates

Once you have defined the assets on the component in one of the two ways above, you can output them in your templates.
This, again, works in the same way as it does for Django form widgets.
The component instance will have a `media` property which returns an instance of the `django.forms.Media` class.
This is the case, even if you used the nested `Media` class to define the assets.
The [string representation of a `Media` objects](https://docs.djangoproject.com/en/5.0/topics/forms/media#s-media-objects) are the HTML declarations to include the assets.

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

#### Combining media with `MediaContainer`

When you have many components in a page, it can be cumbersome to output the media declarations for each component individually.
To make that process a bit easier, Laces provides a `MediaContainer` class.
The `MediaContainer` class is a subclass of Python's built-in `list` class which combines the `media` of all it's members.

In a view we can create a `MediaContainer` instance containing several media-defining components and pass it to the view template.

```python
# my_app/views.py

from django.shortcuts import render
from laces.components import MediaContainer

from my_app.components import (
    Dashboard,
    Footer,
    Header,
    Sidebar,
    WelcomePanel,
)


def home(request):
    components = MediaContainer(
        [
            Header(),
            Sidebar(),
            WelcomePanel(),
            Dashboard(),
            Footer(),
        ]
    )

    return render(
        request,
        "my_app/home.html",
        {
            "components": components,
        },
    )
```

Then, in the view template, we can output the media declarations for all components in the container at once.

```html+django
{# my_app/templates/my_app/home.html #}

{% load laces %}

<head>
    {{ components.media }}
<head>
<body>
    {% for component in components %}
        {% component component %}
    {% endfor %}
</body>
```

This will output a combined media declaration for all components in the container.
The combination of the media declarations follows the behaviour outlined in the [Django documentation](https://docs.djangoproject.com/en/5.0/topics/forms/media/#combining-media-objects).

**Note**:
The use of `MediaContainer` is not limited to contain components.
It can be used to combine the `media` properties of any kind of objects that have a `media` property.

## Patterns for using components

Below, we want to show a few more examples of how components can be used that were not covered in the ["Getting started" section](#getting-started) above.

### Nesting components

The combination of data and template that components provide becomes especially useful when components are nested.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component): ...


class Dashboard(Component):
    template_name = "my_app/components/dashboard.html"

    def __init__(self, user):
        self.welcome = WelcomePanel(name=user.first_name)
        ...

    def get_context_data(self, parent_context):
        return {"welcome": self.welcome}
```

The template of the "parent" component does not need to know anything about the "child" component, except for which template variable is a component.
The child component already contains the data it needs and knows which template to use to render that data.

```html+django
{# my_app/templates/my_app/components/dashboard.html #}

{% load laces %}

<div class="dashboard">
    {% component welcome %}

    ...
</div>
```

The nesting also provides us with a nice data structure we can test.

```python
dashboard = Dashboard(user=request.user)

assert dashboard.welcome.name == request.user.first_name
```

### Nested groups of components

The nesting of components is not limited to single instances.
We can also nest groups of components.

```python
# my_app/components.py

from laces.components import Component


class WelcomePanel(Component): ...


class UsagePanel(Component): ...


class TeamPanel(Component): ...


class Dashboard(Component):
    template_name = "my_app/components/dashboard.html"

    def __init__(self, user):
        self.panels = [
            WelcomePanel(name=user.first_name),
            UsagePanel(user=user),
            TeamPanel(groups=user.groups.all()),
        ]
        ...

    def get_context_data(self, parent_context):
        return {"panels": self.panels}
```

```html+django
{# my_app/templates/my_app/components/dashboard.html #}

{% load laces %}

<div class="dashboard">
    {% for panel in panels %}
        {% component panel %}
    {% endfor %}
    ...
</div>
```

### Container components

The [above example](#nested-groups-of-components) is relatively static.
The `Dashboard` component always contains the same panels.

You could also imagine passing the child components in through the constructor.
This would make your component into a dynamic container component.

```python
# my_app/components.py

from laces.components import Component


class Section(Component):
    template_name = "my_app/components/section.html"

    def __init__(self, children: list[Component]):
        self.children = children
        ...

    def get_context_data(self, parent_context):
        return {"children": self.children}


class Heading(Component): ...


class Paragraph(Component): ...


class Image(Component): ...
```

```html+django
{# my_app/templates/my_app/components/section.html #}

{% load laces %}
<section>
    {% for child in children %}
        {% component child %}
    {% endfor %}
</section>
```

The above `Section` component can take any kind of component as children.
The only thing that `Section` requires is that the children can be rendered with the `{% component %}` tag (which all components do).

In the view, we can now instantiate the `Section` component with any children we want.

```python
# my_app/views.py

from django.shortcuts import render

from my_app.components import (
    Heading,
    Image,
    Paragraph,
    Section,
)


def home(request):
    content = Section(
        children=[
            Heading(...),
            Paragraph(...),
            Image(...),
        ]
    )

    return render(
        request,
        "my_app/home.html",
        {"content": content},
    )
```

```html+django
{# my_app/templates/my_app/home.html #}

{% load laces %}

<body>
    {% component content %}
    ...
</body>
```

### Using dataclasses

Above, we showed how to [use class properties](#using-class-properties) to add data to the component's context.
This is a very useful and common pattern.
However, it is a bit verbose, especially when you have many properties and directly pass the properties to the template context.

To make this a little more convenient, we can use [`dataclasses`](https://docs.python.org/3.12/library/dataclasses.html#module-dataclasses).

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
Then, we can use the `asdict` function to convert the dataclass instance to a dictionary that can be directly as the template context.

The `asdict` function only adds keys to the dictionary that were defined as the properties defined in the dataclass.
In the above example, the dictionary returned by `asdict` would only contain the `name` key.
It would not contain the `template_name` key, because that is set on the class with a value but without a type annotation.
If you were to add the type annotation, then the `template_name` key would also be included in the dictionary returned by `asdict`.

### Custom constructor methods

When a component has many properties, it can be a pain to pass each property to the constructor individually.
This is especially true when the component is used in many places and the data preparation would need to be repeated in each use case.
Custom constructor methods can help with that.

In case of our `WelcomePanel` example, we might want to show some more user information, including a profile image and link to the user's profile page.
We can add a `classmethod` that takes the user object and returns an instance of the component with all the data needed to render the component.
We can also use this method to encapsulate the logic for generating additional data, such as the profile URL.

```python
# my_app/components.py

from django import urls
from dataclasses import dataclass, asdict

from laces.components import Component


@dataclass
class WelcomePanel(Component):
    template_name = "my_app/components/welcome.html"

    first_name: str
    last_name: str
    profile_url: str
    profile_image_url: str

    @classmethod
    def from_user(cls, user):
        profile_url = urls.reverse("profile", kwargs={"pk": user.pk})
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            profile_url=profile_url,
            profile_image_url=user.profile.image.url,
        )

    def get_context_data(self, parent_context):
        return asdict(self)
```

Now, we can instantiate the component in the view like so:

```python
# my_app/views.py

from django.shortcuts import render

from my_app.components import WelcomePanel


def home(request):
    welcome = WelcomePanel.from_user(request.user)
    return render(
        request,
        "my_app/home.html",
        {"welcome": welcome},
    )
```

The constructor method allows us to keep our view very simple and clean as all the data preparation is encapsulated in the component.

As in the example above, custom constructor methods pair very well with the use of dataclasses, but they can of course also be used without them.

## About Laces

### Laces and Wagtail

As mentioned in the introduction, the Laces package was extracted from [Wagtail](https://pypi.org/project/wagtail/) to make it available to the wider Django ecosystem.
The Wagtail documentation still contains the section on what was called originally called ["Template Components"](https://docs.wagtail.org/en/v6.0.1/extending/template_components.html).
While the code for these components was defined in submodules of the `wagtail.admin` module, there was no limitation on them being only used in the Wagtail admin.

As of [Wagtail release 6.0](https://docs.wagtail.org/en/stable/releases/6.0.html#other-maintenance), Wagtail includes Laces as a dependency.
The original implementations of `Component` and `MediaContainer` classes as well as the `{% component %}` template tag have been replaced by imports of the equivalents from Laces.
The names are still available at their original import locations, `wagtail.admin.ui.components` and `wagtail.admin.templatetags.wagtailadmin_tags` respectively.
So, if you have been using these imports before, no change is needed, they still work.

If you want to start using components in a Wagtail project, you can use the Wagtail or Laces import paths interchangeably.
To be able to use the Laces template tag library with `{% load laces %}`, you need to add `laces` you your `INSTALLED_APPS`.

If you want to start using components with Wagtail on a release before 6.0, it is probably best to stick with the Wagtail imports.
This guarantees you won't run into any conflicts when upgrading.
All the patterns shown above should work regardless, only the import paths are different.

### Why "Laces"?

"Laces" is somewhat of a reference to the feature of tying data and templates together.
The components are also "self-rendering," which could be seen as "self-reliance," which relates to "bootstrapping."
And while "bootstraps" aren't really "(shoe) laces," my mind made the jump anyhow.

Finally, it is a nod to [@mixxorz](https://github.com/mixxorz)'s fantastic [Slippers package](https://github.com/mixxorz/slippers), which also takes a component focused approach to improve the experience when working with Django templates, but in a quite different way.

### Supported versions

- Python >= 3.8
- Django >= 3.2

## Contributing

### Install

To make changes to this project, first clone this repository:

```sh
$ git clone https://github.com/tbrlpld/laces.git
$ cd laces
```

With your preferred virtualenv activated, install the development dependencies:

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
$ tox -e python3.11-django4.2
```

Or, run only a specific test:

```sh
$ tox -e python3.11-django4.2 laces.tests.test_file.TestClass.test_method
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

#### Running tests without `tox`

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
To ensure that `tox` will find Python versions installed with `pyenv` you need [`virtualenv-pyenv`](https://pypi.org/project/virtualenv-pyenv/) (note: this is not `pyenv-virtualenv`).
`virtualenv-pyenv` is part of the development dependencies (just like `tox` itself).
Additionally, you have to set the environment variable `VIRTUALENV_DISCOVERY=pyenv`.

### Publishing

This project uses the [Trusted Publisher model for PyPI releases](https://docs.pypi.org/trusted-publishers/).
This means that publishing is done through GitHub Actions when a [new release is created on GitHub](https://github.com/tbrlpld/laces/releases/new).

Before publishing a new release, make sure to update

- [ ] the changelog in `CHANGELOG.md`, and
- [ ] the version number in `laces/__init__.py`.

To update these files, you will have to create a release-prep branch and PR.
Once that PR is merged into `main` you are ready to create the release.

To manually test publishing the package, you can use `flit`.
Be sure to configure the `testpypi` repository in your `~/.pypirc` file according to the Flit [documentation](https://flit.pypa.io/en/stable/upload.html#controlling-package-uploads).
If your PyPI account is using 2FA, you'll need to create a [PyPI API token](https://test.pypi.org/help/#apitoken) and use that as your password and `__token__` as the username.

When you're ready to test the publishing, run:

```shell
$ flit build
$ flit publish --repository testpypi
```

Once you are ready to actually release the new version, you need to first create a git tag.
The tag name should be the version number prefixed with a `v` (e.g. `v0.1.0`).

To create the tag on the command line:

```sh
$ git switch main
$ git pull
$ git tag v0.1.1
$ git push --tags
```

Once the tag is on GitHub, you can visit the [Tags screen](https://github.com/tbrlpld/laces/tags).
There you click "create release" in the overflow menu of the tag that you have just created.
On the release screen you can click "generate release notes", which will compile release notes based on the merged PRs since the last release.
Edit the generated release notes to make them a bit more concise (e.g. remove small fix-up PRs or group related changes).

Once the release notes are ready, click "publish release".
This will trigger the release workflow, which you can observe on the ["Actions" tab](https://github.com/tbrlpld/laces/actions).
When the workflow completes, check the new release on [PyPI](https://pypi.org/project/laces/).

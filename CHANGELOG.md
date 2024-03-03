# Laces Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD

### Added

- Added section on "Laces and Wagtail" to README. ([#26](https://github.com/tbrlpld/laces/pull/26))

### Changed

- Refactored handling of `parent_context` between `render_html` and `get_context_data`. This change is Wagtail-compatible. ([#24](https://github.com/tbrlpld/laces/pull/24))

### Removed

- ...

## [0.1.1] - 2024-02-10

### Added

- Added more tests and example usage. ([#6](https://github.com/tbrlpld/laces/pull/6))
- Added support for Python 3.12 and Django 5.0. ([#15](https://github.com/tbrlpld/laces/pull/15))
- Added type hints and type checking with `mypy` in CI. ([#18](https://github.com/tbrlpld/laces/pull/18))

### Changed

- Fixed tox configuration to actually run Django 3.2 in CI. Tox also uses the "testing" dependencies without the need to duplicate them in the `tox.ini`. ([#10](https://github.com/tbrlpld/laces/pull/10))
- Bumped GitHub Actions to the latest versions. This removes a reliance on the now deprecated Node 16. ([#10](https://github.com/tbrlpld/laces/pull/10))
- Extend documentation in README to simplify first examples and improve structure. ([#7](https://github.com/tbrlpld/laces/pull/7))

## [0.1.0] - 2023-11-29

### Added

- Extracted component related code from [Wagtail](https://pypi.org/project/wagtail/) project for reuse.

<!-- TEMPLATE - keep below to copy for new releases -->
<!--

## [Unreleased] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Removed

- ...

-->

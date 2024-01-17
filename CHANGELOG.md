# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.14] - 2024-01-17

### Added

- Support for Wagtail 5.0+, Django 5.0 ([#29](https://github.com/wagtail/wagtail-localize-git/pull/) @jhonatan-lopes)
- Coverage report to the GitHub Actions summary

### Changed

- Switched to using pyproject.toml and flit for packaging
- Switched to using PyPI trusted publishing via GitHub Actions
- Switched to using Ruff for linting/formatting

## [0.13] - 2022-09-23

### Added

- Support for Wagtail 4, wagtail-localize 1.2+ ([#26](https://github.com/wagtail/wagtail-localize-git/pull/26))

### Changed

- Dropped support for Wagtail < 2.15
- Relaxed the wagtail-localize version constraints

## [0.12] - 2022-02-03

### Breaking changes
This release will use `main` as the default branch. To change it anything else, use `WAGTAILLOCALIZE_GIT_DEFAULT_BRANCH = "my-branch"` in your settings file

### Added
- Support for configurable mainline branch, with a default of `main` ([#21](https://github.com/wagtail/wagtail-localize-git/pull/21))
- Ability to install with Wagtail 2.16 ([#23](https://github.com/wagtail/wagtail-localize-git/pull/23))
  Note: can be installed on Wagtail 2.16 with wagtail-localize >= 1.1
- A sync retry mechanism on push failures ([#24](https://github.com/wagtail/wagtail-localize-git/pull/24))
  Sync will retry up to 3 times before throwing a `SyncPushError` exception

## [0.11] - 2021-12-02

### Added

- [Support for Wagtail 2.15](https://github.com/wagtail/wagtail-localize-git/pull/17)
- Testing with Python 3.9 and 3.10 ([#17](https://github.com/wagtail/wagtail-localize-git/pull/17), [#18](https://github.com/wagtail/wagtail-localize-git/pull/18))

## [0.10] - 2021-09-28

### Added

 - [Support for Wagtail 2.14](https://github.com/wagtail/wagtail-localize-git/pull/15)

[unreleased]: https://github.com/wagtail/wagtail-localize-git/compare/v0.14.0...HEAD
[0.14]: https://github.com/wagtail/wagtail-localize-git/compare/v0.13.0...v0.14.0
[0.13]: https://github.com/wagtail/wagtail-localize-git/compare/v0.12.0...v0.13.0
[0.12]: https://github.com/wagtail/wagtail-localize-git/compare/v0.11.0...v0.12.0
[0.11]: https://github.com/wagtail/wagtail-localize-git/compare/v0.10.0...v0.11.0
[0.10]: https://github.com/wagtail/wagtail-localize-git/compare/v0.9.3...v0.10.0

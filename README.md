# wagtail-localize-git

This plugin enables translating Wagtail content using a PO files in a git repository.

It works by committing source content into the repository then polling it for updates. When the PO files are translated, this will automatically create translated pages in Wagtail.

This is useful for when you are using external translation tools for translating your Wagtail content. Currently, this plugin supports Mozilla's [Pontoon](https://pontoon.mozilla.org/), but PRs are welcome for other translation tools!

## Installation

This plugin requires Wagtail 2.11 with [internationalisation enabled](https://docs.wagtail.io/en/v2.11/advanced_topics/i18n.html#configuration) and [Wagtail Localize](https://github.com/wagtail/wagtail-localize).

Install both `wagtail-localize` and `wagtail-localize-git`, then add the following to your `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "wagtail_localize",
    "wagtail_localize.locales",  # Replaces 'wagtail.locales'
    "wagtail_localize_git",
    # ...
]
```

Then set the following settings:

`WAGTAILLOCALIZE_GIT_URL` - This is a URL to an empty git repository that `wagtail-localize-git` will push source strings to and fetch translations from.
`WAGTAILLOCALIZE_GIT_CLONE_DIR` - The local directory where the git repository will be checked out.

## Synchronisation

Once this is configured, you can use the `sync_git` management command to push/pull changes. This management command should be set up in your server's crontab to run often (preferably, every 10 minutes).

## How it works

This plugin uses `wagtail-localize` to convert pages into segments and build new pages from translated segments. `wagtail-localize` provides a web interface for translating these segments in Wagtail itself and this plugin plays nicely with that (translations can be made from the Wagtail side too).

Pages/snippets are submitted to the git repo when they are submitted for translation from the default locale. Pages authored in other locales are not supported yet.

## Contributing

All contributions are welcome!

### Install

To make changes to this project, first clone this repository:

```sh
git clone git@github.com:wagtail/wagtail-localize-git.git
cd wagtail-localize-git
```

With your preferred virtualenv activated, install testing dependencies:

```sh
pip install -e .[testing] -U
```

### pre-commit

Note that this project uses [pre-commit](https://github.com/pre-commit/pre-commit). To set up locally:

```shell
# if you don't have it yet, globally
$ pip install pre-commit
# go to the project directory
$ cd wagtail-localize-git
# initialize pre-commit
$ pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
$ pre-commit run --all-files
```

### How to run tests

Now you can run tests as shown below:

```sh
tox
```

or, you can run them for a specific environment `tox -e python3.9-django3.2-wagtail2.15` or specific test
`tox -e python3.9-django3.2-wagtail2.15-sqlite wagtail_localize_git.tests.test_git.TestRepository`

To run the test app interactively, use `tox -e interactive`, visit `http://127.0.0.1:8020/admin/` and log in with `admin`/`changeme`.

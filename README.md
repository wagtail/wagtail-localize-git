# wagtail-localize-pontoon

Use [Pontoon](https://pontoon.mozilla.org/) as a translation engine for [wagtail-localize](https://github.com/kaedroho/wagtail-localize).

## Installation

Install both `wagtail-localize` and `wagtail-localize-pontoon`, then add the following to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'wagtail_localize',
    'wagtail_localize.translation_memory',
    'wagtail_localize_pontoon',
    ...
]
```

Then set the following settings:

`WAGTAILLOCALIZE_PONTOON_GIT_URL` - This is a URL to an empty git repository where `wagtail-localize-pontoon` will push source strings and Pontoon will push back translations.
`WAGTAILLOCALIZE_PONTOON_GIT_CLONE_DIR` - The local directory where the git repository will be checked out.

## Configuring page types

Any page types that need to be translatable must inherit from `TranslatablePageMixin` and have `translated_fields` set to a list of field
names that are translatable.

To migrate existing page types to be translatable, use the `BootstrapTranslatableMixin` clas sfrom `wagtail-localize` to help create the migrations. See docstring on that class for details.

## Running initial sync

Firstly run the `sync_languages` command. This creates `Language` objects for all the languages defined in your `LANGUAGES` setting.

Then run the `submit_whole_site_to_pontoon` management command. This generates submissions for all live translatable pages on the site.

Then finally run the `sync_pontoon` management command. This pushes the source strings to Pontoon.

## How it works

This relies heavily on `wagtail-localize`'s `translation_memory` module to track which source strings need to be translated in order to create/update a translated version of a page.

### Creating submissions

When the user publishes an english version of the page, the following steps happen:

 - All translatable segments are extracted from the page and saved in the `translation_memory.Segment` model. This model holds unique source strings, the locations these strings appear on pages is stored in the `translation_memory.SegmentPageLocation` model.
 - A `wagtail_localize_pontoon.PontoonResourceSubmission` object is created to note which page revision needs to be submitted to Pontoon.

The `submit_whole_site_to_pontoon` command runs this process for all live translatable pages.

### Pushing source strings to Pontoon

The `sync_pontoon` command firstly fetches the git repo, then checks for and imports any translated strings. More about this later.

After this, it will write all of the source and locale `.po` files based on the records in `PontoonResourceSubmission` and the segments/translations in translation memory.

Any new strings are added into both the source `.pot` file and each locale-specific `.po` file, this is because Pontoon will not send back any
translations unless the source string is also added into each locale-specific `.po` file.

If a string is no longer used on a page, it is removed from the source `.pot` file, but may be left in the locale-specific `.po` files if a translation existed for that string but will be flagged as obsolete.

### Pulling translations from Pontoon

At the beginning of the `sync_pontoon` command, the git repo is fetched and if there are any changes, a diff is performed between the new remote `HEAD` and the local `HEAD`.

If any of the locale PO files have been modified, they will be parsed and any new/changed translations saved in the `translation_memory.SegmentTranslation` model.

After a locale PO file is imported, it then checks the translation progress of that page/language by making a query against the `translation_memory` models, if it is ready, it creates or updates the translated version of the page.

If a page is ready to be translated, but it's parent is not translated into the target language, the translation is delayed until the parent is translated and will be done automatically when this has happend.


### Caveats

- Any edits on translated pages will be overwritten if the original page is updated and translated again.
- If a page is translated but one of the strings is edited in pontoon, the new version of the string will not be pulled through automatically. The original page should be re-submitted to Pontoon again first.

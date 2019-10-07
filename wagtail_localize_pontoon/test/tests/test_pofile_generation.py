import logging

import polib
from django.test import TestCase

from wagtail.core.models import Page
from wagtail_localize.models import Language
from wagtail_localize.translation_memory.models import Segment, SegmentTranslation, SegmentPageLocation

from wagtail_localize_pontoon.models import PontoonResource
from wagtail_localize_pontoon.pofile import generate_source_pofile, generate_language_pofile

from ..models import TestPage


def create_test_page(**kwargs):
    root_page = Page.objects.get(id=1)
    page = root_page.add_child(instance=TestPage(**kwargs))
    revision = page.save_revision()
    revision.publish()
    return page


class TestImporter(TestCase):
    def setUp(self):
        self.page = create_test_page(
            title="Test page",
            slug='test-page',
            test_translatable_field="The test translatable field",
            test_synchronized_field="The test synchronized field",
        )
        self.resource = PontoonResource.objects.get(page=self.page)
        self.language = Language.objects.create(code='fr')

    def test_generate_source_pofile(self):
        pofile = generate_source_pofile(self.resource)
        parsed_po = polib.pofile(pofile)
        self.assertEqual(
            [(m.msgid, m.msgstr) for m in parsed_po],
            [
                ("The test translatable field" , ""),
            ]
        )

    def test_generate_language_pofile(self):
        pofile = generate_language_pofile(self.resource, self.language)
        parsed_po = polib.pofile(pofile)
        self.assertEqual(
            [(m.msgid, m.msgstr) for m in parsed_po],
            [
                ("The test translatable field" , ""),
            ]
        )

    def test_generate_language_pofile_with_existing_translation(self):
        segment = Segment.objects.get(text="The test translatable field")
        SegmentTranslation.objects.create(
            translation_of=segment,
            language=self.language,
            text="Le champ traduisible de test",
        )

        pofile = generate_language_pofile(self.resource, self.language)
        parsed_po = polib.pofile(pofile)
        self.assertEqual(
            [(m.msgid, m.msgstr) for m in parsed_po],
            [
                ("The test translatable field" , "Le champ traduisible de test"),
            ]
        )

    def test_generate_language_pofile_with_existing_obsolete_translation(self):
        # Update the existing segment. The save_revision bit below will generate a new segment with the current text
        segment = Segment.objects.get()
        segment.text = "Some obsolete text"
        segment.text_id = Segment.get_text_id(segment.text)
        segment.save()

        SegmentTranslation.objects.create(
            translation_of=segment,
            language=self.language,
            text="Du texte obsolète",
        )

        # Create a new revision. This will create a new segment like how the current segment was before I changed it
        # It will also update the revision field on the resource so we need to refresh that
        self.page.save_revision().publish()
        self.resource.refresh_from_db()

        pofile = generate_language_pofile(self.resource, self.language)
        parsed_po = polib.pofile(pofile)
        self.assertEqual(
            [(m.msgid, m.msgstr, m.obsolete) for m in parsed_po],
            [
                ("The test translatable field" , "", 0),
                ("Some obsolete text" , "Du texte obsolète", 1),
            ]
        )

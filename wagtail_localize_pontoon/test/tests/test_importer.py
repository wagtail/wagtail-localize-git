import logging

import polib
from django.test import TestCase
from django.utils import timezone

from wagtail.core.models import Page
from wagtail_localize.models import Language

from wagtail_localize_pontoon.importer import Importer
from wagtail_localize_pontoon.models import PontoonResource, PontoonSyncLog

from ..models import TestPage


def create_test_page(**kwargs):
    root_page = Page.objects.get(id=1)
    page = root_page.add_child(instance=TestPage(**kwargs))
    revision = page.save_revision()
    revision.publish()
    return page


def create_test_po(entries):
    po = polib.POFile(wrapwidth=200)
    po.metadata = {
        'POT-Creation-Date': str(timezone.now()),
        'MIME-Version': '1.0',
        'Content-Type': 'text/html; charset=utf-8',
    }

    for entry in entries:
        po.append(
            polib.POEntry(
                msgid=entry[0],
                msgstr=entry[1],
            )
        )

    return str(po)


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

    def test_importer(self):
        with self.subTest(stage="New page"):
            po_v1 = create_test_po([
                ("The test translatable field", ""),
            ]).encode('utf-8')

            po_v2 = create_test_po([
                ("The test translatable field", "Le champ traduisible de test"),
            ]).encode('utf-8')

            importer = Importer(Language.objects.default(), logging.getLogger('dummy'))
            importer.start_import('0' * 40)
            importer.import_file(self.resource.get_po_filename(language=self.language), po_v1, po_v2)

            # Check translated page was created
            translated_page = TestPage.objects.get(locale__language=self.language)
            self.assertEqual(translated_page.translation_key, self.page.translation_key)
            self.assertFalse(translated_page.is_source_translation)
            self.assertEqual(translated_page.test_translatable_field, "Le champ traduisible de test")
            self.assertEqual(translated_page.test_synchronized_field, "The test synchronized field")

            # Check log
            log = PontoonSyncLog.objects.get()
            self.assertEqual(log.action, PontoonSyncLog.ACTION_PULL)
            self.assertEqual(log.commit_id, '0' * 40)
            log_resource = log.resources.get()
            self.assertEqual(log_resource.resource, self.resource)
            self.assertEqual(log_resource.language, self.language)

        # Perform another import updating the page
        # Much easier to do it this way than trying to construct all the models manually to match the result of the last test
        with self.subTest(stage="Update page"):
            po_v3 = create_test_po([
                ("The test translatable field", "Le champ testable à traduire avec un contenu mis à jour"),
            ]).encode('utf-8')

            importer = Importer(Language.objects.default(), logging.getLogger('dummy'))
            importer.start_import('0' * 39 + '1')
            importer.import_file(self.resource.get_po_filename(language=self.language), po_v2, po_v3)

            translated_page.refresh_from_db()
            self.assertEqual(translated_page.translation_key, self.page.translation_key)
            self.assertFalse(translated_page.is_source_translation)
            self.assertEqual(translated_page.test_translatable_field, "Le champ testable à traduire avec un contenu mis à jour")
            self.assertEqual(translated_page.test_synchronized_field, "The test synchronized field")

            # Check log
            log = PontoonSyncLog.objects.exclude(id=log.id).get()
            self.assertEqual(log.action, PontoonSyncLog.ACTION_PULL)
            self.assertEqual(log.commit_id, '0' * 39 + '1')
            log_resource = log.resources.get()
            self.assertEqual(log_resource.resource, self.resource)
            self.assertEqual(log_resource.language, self.language)

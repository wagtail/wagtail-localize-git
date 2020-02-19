from django.test import TestCase
from wagtail.core.models import Page

from wagtail_localize.test.models import TestPage

from wagtail_localize_pontoon.models import PontoonResource


def create_test_page(**kwargs):
    parent = kwargs.pop("parent", None) or Page.objects.get(id=1)
    page = parent.add_child(instance=TestPage(**kwargs))
    revision = page.save_revision()
    revision.publish()
    return page


class AutoSubmitTestCase(TestCase):
    def assert_submitted(self, page):
        self.assertTrue(
            PontoonResource.objects.filter(
                object__translation_key=page.translation_key
            ).exists()
        )

    def assert_not_submitted(self, page):
        self.assertFalse(
            PontoonResource.objects.filter(
                object__translation_key=page.translation_key
            ).exists()
        )

    def test_auto_submits(self):
        # Auto-submit is on by default
        page = create_test_page(title="Test Page", slug="test-page")

        self.assert_submitted(page)

    def test_doesnt_auto_submit_with_submit_to_pontoon_on_publish_false(self):
        try:
            TestPage.submit_to_pontoon_on_publish = False
            page = create_test_page(title="Test Page", slug="test-page")

        finally:
            delattr(TestPage, "submit_to_pontoon_on_publish")

        self.assert_not_submitted(page)

    def test_doesnt_auto_submit_with_submit_to_pontoon_on_publish_callable_false(self):
        try:

            def dont_submit(self):
                return False

            TestPage.submit_to_pontoon_on_publish = dont_submit
            page = create_test_page(title="Test Page", slug="test-page")

        finally:
            delattr(TestPage, "submit_to_pontoon_on_publish")

        self.assert_not_submitted(page)
git

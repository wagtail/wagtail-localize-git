from django.db import models

from wagtail.core.models import Page
from wagtail_localize.fields import TranslatableField, SynchronizedField
from wagtail_localize.models import TranslatablePageMixin


class TestPage(TranslatablePageMixin, Page):
    test_translatable_field = models.TextField(blank=True)
    test_synchronized_field = models.TextField(blank=True)

    translatable_fields = [
        TranslatableField("test_translatable_field"),
        SynchronizedField("test_synchronized_field"),
    ]

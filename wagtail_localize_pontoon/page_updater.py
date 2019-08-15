from django.utils.text import slugify

from wagtail.core.models import Page
from wagtail_localize.models import Locale, Region
from wagtail_localize.segments import SegmentValue, TemplateValue
from wagtail_localize.segments.ingest import ingest_segments
from wagtail_localize.translation_memory.models import SegmentPageLocation, TemplatePageLocation


def create_or_update_translated_page(revision, language):
    locale = Locale.objects.get(region_id=Region.objects.default_id(), language=language)

    page = revision.as_page_object()

    try:
        translated_page = page.get_translation(locale)
        created = False
    except page.specific_class.DoesNotExist:
        # May raise ParentNotTranslatedError
        translated_page = page.copy_for_translation(locale)
        created = True

    # Fetch all translated segments
    segment_page_locations = (
        SegmentPageLocation.objects
        .filter(page_revision=revision)
        .annotate_translation(language)
    )

    template_page_locations = (
        TemplatePageLocation.objects
        .filter(page_revision=revision)
        .select_related('template')
    )

    segments = []

    for page_location in segment_page_locations:
        segment = SegmentValue(page_location.path, page_location.translation)
        segments.append(segment)

    for page_location in template_page_locations:
        template = page_location.template
        segment = TemplateValue(page_location.path, template.template_format, template.template, template.segment_count)
        segments.append(segment)

    # Ingest all translated segments into page
    ingest_segments(page, translated_page, page.locale.language, language, segments)

    # Make sure the slug is valid
    translated_page.slug = slugify(translated_page.slug)
    translated_page.save()

    new_revision = translated_page.save_revision()
    new_revision.publish()

    return new_revision, created

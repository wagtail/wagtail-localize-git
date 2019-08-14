import polib
from django.utils import timezone


def generate_source_pofile(resource):
    """
    Generate a source PO file for the given resource
    """
    po = polib.POFile(wrapwidth=200)
    po.metadata = {
        'POT-Creation-Date': str(timezone.now()),
        'MIME-Version': '1.0',
        'Content-Type': 'text/html; charset=utf-8',
    }

    for segment in resource.get_segments().iterator():
        po.append(
            polib.POEntry(
                msgid=segment.text,
                msgstr='',
            )
        )

    return str(po)


def generate_language_pofile(resource, language):
    """
    Generate a translated PO file for the given resource/language
    """
    po = polib.POFile(wrapwidth=200)
    po.metadata = {
        'POT-Creation-Date': str(timezone.now()),
        'MIME-Version': '1.0',
        'Content-Type': 'text/html; charset=utf-8',
        'Language': language.as_rfc5646_language_tag(),
    }

    for segment in resource.get_segments(include_obsolete=True, annotate_obsolete=True).annotate_translation(language).iterator():
        # Filter out obsolete entries that haven't been translated
        # TODO: Do this in SQL query
        if segment.is_obsolete and segment.translation is None:
            continue

        po.append(
            polib.POEntry(
                msgid=segment.text,
                msgstr=segment.translation or '',
                obsolete=segment.is_obsolete,
            )
        )

    return str(po)

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils import timezone
import polib

from wagtail_localize.models import Language, Locale, ParentNotTranslatedError
from wagtail_localize.translation_memory.models import Segment

from ...git import Repository
from ...models import PontoonResourceSubmission, PontoonResource
from ...pofile import generate_source_pofile, generate_language_pofile


def try_update_resource_translation(resource, language):
    # Check if there is a submission ready to be translated
    translatable_submission = resource.find_translatable_submission(language)

    if translatable_submission:
        print(f"Saving translated page for '{resource.page.title}'")

        try:
            revision, created = translatable_submission.create_or_update_translated_page(language)
        except ParentNotTranslatedError:
            # These pages will be handled when the parent is created in the code below
            print("Unable to save translated page as its parent must be translated first")

        if created:
            # Check if this page has any children that may be ready to translate
            child_page_resources = PontoonResource.objects.filter(
                page__in=revision.page.get_children()
            )

            for resource in child_page_resources:
                try_update_resource_translation(resource, language)


class Command(BaseCommand):

    def handle(self, **options):
        repo = Repository.open()

        # Pull changes from repo
        merger = repo.pull()

        for filename, old_content, new_content in merger.changed_files():
            print("Ingesting changes for", filename)
            resource, language = PontoonResource.get_by_po_filename(filename)
            old_po = polib.pofile(old_content.decode('utf-8'))
            new_po = polib.pofile(new_content.decode('utf-8'))

            with transaction.atomic():
                for changed_entry in set(new_po) - set(old_po):
                    try:
                        segment = Segment.objects.get(text=changed_entry.msgid)
                        translation, created = segment.translations.get_or_create(
                            language=language,
                            defaults={
                                'text': changed_entry.msgstr,
                                'updated_at': timezone.now(),
                            }
                        )

                        if not created:
                            # Update the translation only if the text has changed
                            if translation.text != changed_entry.msgstr:
                                translation.text = changed_entry.msgstr
                                translation.updated_at = timezone.now()
                                translation.save()

                                # TODO: Update previously translated pages that used this string?

                    except Segment.objects.DoesNotExist:
                        print("Warning: unrecognised segment")

                # Check if the translated page is ready to be created/updated
                try_update_resource_translation(resource, language)

        merger.commit()

        # Push our changes
        reader = repo.reader()
        writer = repo.writer()
        writer.copy_unmanaged_files(reader)

        def update_po(filename, new_po_string):
            try:
                current_po_string = reader.read_file(filename).decode('utf-8')
                current_po = polib.pofile(current_po_string, wrapwidth=200)

                # Take metadata from existing PO file
                new_po = polib.pofile(new_po_string, wrapwidth=200)
                new_po.metadata = current_po.metadata
                new_po_string = str(new_po)

            except KeyError:
                pass

            writer.write_file(filename, new_po_string)

        languages = Language.objects.filter(is_active=True).exclude(id=Language.objects.default_id())

        with transaction.atomic():
            paths = []
            pushed_submission_ids = []
            for submission in PontoonResourceSubmission.objects.filter(revision_id=F('resource__current_revision_id')).select_related('resource').order_by('resource__path'):
                source_po = generate_source_pofile(submission.resource)
                update_po(str(submission.resource.get_po_filename()), source_po)

                for language in languages:
                    locale_po = generate_language_pofile(submission.resource, language)
                    update_po(str(submission.resource.get_po_filename(language=language)), locale_po)

                paths.append((submission.resource.get_po_filename(), submission.resource.get_locale_po_filename_template()))

                pushed_submission_ids.append(submission.id)

            PontoonResourceSubmission.objects.filter(id__in=pushed_submission_ids).update(pushed_at=timezone.now())

            writer.write_config([language.as_rfc5646_language_tag() for language in languages], paths)

            if writer.has_changes():
                print("Committing changes")
                writer.commit("Updates to source content")
                repo.push()

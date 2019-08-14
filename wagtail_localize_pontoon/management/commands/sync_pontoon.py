from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils import timezone
import polib

from wagtail_localize.models import Language, Locale
from wagtail_localize.translation_memory.models import Segment

from ...git import Repository
from ...models import PontoonResourceSubmission, PontoonResource
from ...pofile import generate_source_pofile, generate_language_pofile


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

            for changed_entry in set(new_po) - set(old_po):
                try:
                    segment = Segment.objects.get(text=changed_entry.msgid)
                    segment.translations.update_or_create(
                        language=language,
                        defaults={
                            'text': changed_entry.msgstr,
                        }
                    )
                except Segment.objects.DoesNotExist:
                    print("Warning: unrecognised segment")

        merger.commit()

        # Push our changes
        reader = repo.reader()
        writer = repo.writer()

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
                repo.try_push()





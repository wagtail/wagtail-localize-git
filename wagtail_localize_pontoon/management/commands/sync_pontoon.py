import logging

from django.core.management.base import BaseCommand

from ...sync import sync, logger


class Command(BaseCommand):

    def handle(self, **options):
        # Enable logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(console)
        logger.setLevel(logging.INFO)

        sync()

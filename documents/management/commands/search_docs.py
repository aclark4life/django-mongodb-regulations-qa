# documents/management/commands/search_docs.py
from django.core.management.base import BaseCommand

from documents.services.search_service import semantic_search


class Command(BaseCommand):
    help = "Run a plain-text search."

    def add_arguments(self, parser):
        parser.add_argument("question")

    def handle(self, *args, **options):
        for hit in semantic_search(options["question"]):
            self.stdout.write(
                f"{hit['score']:.3f}  {hit['document_number']}  {hit['title'][:80]}"
            )
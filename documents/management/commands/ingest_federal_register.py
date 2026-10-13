# documents/management/commands/ingest_federal_register.py
import re
import time

import requests
from django.core.management.base import BaseCommand

from documents.models import Document

API_URL = "https://www.federalregister.gov/api/v1/documents.json"
TAG_PATTERN = re.compile(r"<[^>]+>")


class Command(BaseCommand):
    help = "Load Federal Register documents into MongoDB."

    def add_arguments(self, parser):
        parser.add_argument("--agency", default="environmental-protection-agency")
        parser.add_argument("--limit", type=int, default=300)

    def handle(self, *args, **options):
        params = [
            ("conditions[agencies][]", options["agency"]),
            ("conditions[type][]", "RULE"),
            ("conditions[type][]", "PRORULE"),
            ("per_page", "100"),
        ]
        headers = {"User-Agent": "regulations-qa-tutorial"}
        url, saved = API_URL, 0

        while url and saved < options["limit"]:
            response = requests.get(
                url,
                params=params if url == API_URL else None,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            page = response.json()

            for item in page["results"]:
                abstract = TAG_PATTERN.sub("", item.get("abstract") or "").strip()
                if not abstract:
                    continue
                agencies = item.get("agencies") or [{}]
                Document.objects.update_or_create(
                    document_number=item["document_number"],
                    defaults={
                        "title": TAG_PATTERN.sub("", item["title"]),
                        "doc_type": item["type"],
                        "agency": agencies[0].get("name", ""),
                        "publication_date": item["publication_date"],
                        "abstract": abstract,
                        "source_url": item["html_url"],
                    },
                )
                saved += 1
                if saved >= options["limit"]:
                    break

            url = page.get("next_page_url")
            time.sleep(1)

        self.stdout.write(f"Saved {saved} documents.")
from django.core.management.base import BaseCommand

from trojstenid import search
from trojstenid.schools.models import School


class Command(BaseCommand):
    help = "Send schools to Meilisearch for indexing"

    def handle(self, *args, **options):
        self.stdout.write("Indexing schools...")

        schools = []
        for s in School.objects.filter(is_selectable=True).all():
            schools.append(s.to_dict())

        search.client.index("schools").update_settings(
            {
                "filterableAttributes": ["types"],
                "sortableAttributes": ["name", "address"],
                "rankingRules": [
                    "words",
                    "sort",
                    "typo",
                    "proximity",
                    "attribute",
                    "exactness",
                ],
                "synonyms": {
                    "zš": [
                        "základná škola",
                        "základní škola",
                        "elemi iskola",
                        "alapiskola",
                    ],
                    "základná škola": ["zš"],
                    "základní škola": ["zš"],
                    "elemi iskola": ["zš"],
                    "alapiskola": ["zš"],
                    "sš": [
                        "stredná škola",
                        "strední škola",
                        "középiskola",
                        "střední škola",
                    ],
                    "stredná škola": ["sš"],
                    "strední škola": ["sš"],
                    "középiskola": ["sš"],
                    "střední škola": ["sš"],
                },
            }
        )

        search.client.index("schools").add_documents(schools)

        self.stdout.write(self.style.SUCCESS("Schools indexed successfully."))

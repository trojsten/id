import csv
import io

import requests
from django.db import transaction

from trojstenid.schools.models import School, SchoolType

SCHOOL_DB_URL = (
    "https://raw.githubusercontent.com/trojsten/skoly/refs/heads/master/data/final.csv"
)


@transaction.atomic
def sync_schools():
    resp = requests.get(SCHOOL_DB_URL)
    resp.raise_for_status()

    reader = csv.DictReader(io.StringIO(resp.text))
    existing_types = {t.identifier: t for t in SchoolType.objects.all()}

    for row in reader:
        types = row["years"].split(",")
        eduid = int(row["eduid"])
        name = row["name"]
        address = row["address"]

        real_types = []
        for type_ in types:
            if type_ in existing_types:
                real_types.append(existing_types[type_])
                continue

            new_type = SchoolType.objects.create(identifier=type_, name=type_, years=[])
            existing_types[type_] = new_type
            real_types.append(new_type)

        school, _ = School.objects.update_or_create(
            eduid=eduid,
            defaults={
                "name": name,
                "address": address,
            },
        )
        school.types.set(real_types)

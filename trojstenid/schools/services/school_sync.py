import csv
import io
import warnings

import requests
from django.db import transaction

from trojstenid.schools.models import School, SchoolType

SCHOOL_DB_URL = (
    "https://raw.githubusercontent.com/trojsten/skoly/refs/heads/master/data/final.csv"
)
NULL_TYPES = ["zs:9", "ss:4", "gym:8"]


def _get_years_for_type(type_: str) -> list[str]:
    if type_ == "gym:8":
        return [
            "Príma",
            "Sekunda",
            "Tercia",
            "Kvarta",
            "Kvinta",
            "Sexta",
            "Septima",
            "Oktáva",
        ]

    if ":" not in type_:
        return []

    _, length = type_.split(":", 1)
    if not length.isnumeric():
        return []

    return [f"{i + 1}. ročník" for i in range(int(length))]


def create_null_school():
    exists = School.objects.filter(id=-1).exists()
    if exists:
        return

    school = School.objects.create(id=-1, name="Iná škola")
    types = []
    for null_type in NULL_TYPES:
        type_ = SchoolType.objects.filter(identifier=null_type).first()
        if type_ is None:
            warnings.warn(f"School type {null_type} not found.")
            continue
        types.append(type_)

    school.types.set(types)


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

            new_type = SchoolType.objects.create(
                identifier=type_,
                name=type_,
                short=type_,
                years=_get_years_for_type(type_),
            )
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

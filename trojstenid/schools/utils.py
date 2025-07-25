from datetime import date


def date_to_academic_year(date: date) -> int:
    september = date.replace(month=9, day=1)
    if date < september:
        return date.year - 1
    return date.year


def academic_year_start(year: int) -> date:
    return date(year, 9, 1)


def academic_year_end(year: int) -> date:
    return date(year + 1, 8, 31)

from datetime import date

from utils.translation import MONTHS


def get_birthdate(birthday):
    if not birthday or not isinstance(birthday, str):
        return

    try:
        values = [int(d) for d in birthday.split('/')]
    except ValueError:
        return

    if len(values) != 3:
        return
    year = values[2]

    if year < 100:
        year += 1900
    try:
        return date(year, values[1], values[0])
    except ValueError:
        return


def treat_birthday(date):
    if not date or not isinstance(date, str):
        return ''

    date = date.replace('-', '/')
    date = date.replace(' ', '/')
    for month in MONTHS.keys():
        date = date.replace(month, MONTHS[month])
    return date

import re
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation
from itertools import combinations

from brazilnum.cnpj import validate_cnpj
from brazilnum.cpf import validate_cpf
from Levenshtein import distance


MONTHS = {
    'JAN': '01',
    'FEB': '02',
    'FEV': '02',
    'MAR': '03',
    'APR': '04',
    'ABR': '04',
    'MAY': '05',
    'MAI': '05',
    'JUN': '06',
    'JUL': '07',
    'AUG': '08',
    'AGO': '08',
    'SEP': '09',
    'SET': '09',
    'OCT': '10',
    'OUT': '10',
    'NOV': '11',
    'DEC': '12',
    'DEZ': '12',
}


def parse_date(date):
    if not date or not isinstance(date, str):
        return

    patterns = ('%d/%m/%Y', '%d/%m/%y')
    for pattern in patterns:
        try:
            return datetime.strptime(date, pattern).date()
        except (ValueError, TypeError):
            pass

    return None


def parse_decimal(value, ignore_errors=True):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None


def parse_document(value):
    if not isinstance(value, (str, bytes)):
        return None

    cleaned = re.sub(r'\D', '', value)
    if not validate_cnpj(cleaned) and not validate_cpf(cleaned):
        return None

    return cleaned


def treat_birthday(date):
    if not date or not isinstance(date, str):
        return ''

    date = date.replace('-', '/')
    date = date.replace(' ', '/')
    for month in MONTHS.keys():
        date = date.replace(month, MONTHS[month])
    return date


def normalize(value):
    """Normalize accented characters"""
    return ''.join(
        char for char in unicodedata.normalize('NFD', value)
        if unicodedata.category(char) != 'Mn'
    )


def probably_same_entity(values, threshould=3):
    """Uses Levenshtein to determine, from a list of entity names (as strings),
    if these names probably refer to the same entity (but differ, for example,
    due to grammar differences or minor typos)"""
    normalized = (normalize(value.upper()) for value in values)
    pairs = combinations(normalized, 2)
    distances = (distance(*pair) for pair in pairs)
    return max(distances) <= threshould

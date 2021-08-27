import datetime
import dateutil
import unicodedata
import re
import json
from source_object import source_object
from config import STANDARD_DATE_FORMAT


def parse_date(date, format=STANDARD_DATE_FORMAT):
    """
    parses a date to another format
    :param date: the date to parse, can be str or date
    :param format: the format to parse the date to, uses STANDARD_FORMAT from config as default
    :return: the date in new format
    """
    if type(date) == str:
        date =  dateutil.parser.parse(date)

    return date.strftime(format)

def date_now():
    """
    returns current date in the STANDARD_FORMAT
    """
    return parse_date(datetime.datetime.now())

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    value.replace("ä", "ae").replace("Ä", "Ae").replace("ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue").replace("ß", "ss")
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')

 #  titlestring.replace(" ", "_").replace(",", "_").replace(":", "_").replace("ä", "ae").replace("Ä", "Ae").replace("ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue")
  


from datetime import datetime, date
import dateutil
import unicodedata
import re
import logging
import json

#dont change this config without checking if it is a elasticsearch readable date-format (if you use elasticsearch) 
# https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html#strict-date-time
config = {}

class Singleton(object):
    """
    
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


def init_global_config(config_path):
    """
    reads the config
    """
    try:
        with open(config_path, "r") as file:
            global config 
            config = json.load(file)
    except:
        logging.error("configfile not found.")


def parse_date(date):
    """
    parses a date to another format
    :param date: the date to parse, can be str or date
    :param format: the format to parse the date to, uses STANDARD_DATETIME_FORMAT from config as default
    :return: the date in new format
    """
    if type(date) == str:
        date = re.sub(r"[a-zA-Z]+", " ", date)
        date =  dateutil.parser.parse(date)

    return date.strftime(config["STANDARD_DATETIME_FORMAT"])

def date_now():
    """
    returns current datetime in the STANDARD_DATETIME_FORMAT
    """
    return parse_date(datetime.now())

def date_today():
    """
    returns todays date in the STANDARD_DATE_FORMAT
    """
    return date.today().strftime(config["STANDARD_DATE_FORMAT"])


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
  


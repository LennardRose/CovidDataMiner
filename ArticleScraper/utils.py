import datetime
import dateutil
import unicodedata
import re
import json
from source_object import source_object
from Config import STANDARD_FORMAT 

def parse_date(date, format=STANDARD_FORMAT):
    if type(date) == str:
        date =  dateutil.parser.parse(date)

    return date.strftime(format)

def date_now():
    return parse_date(datetime.datetime.now())

"""
Taken from https://github.com/django/django/blob/master/django/utils/text.py
Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
dashes to single dashes. Remove characters that aren't alphanumerics,
underscores, or hyphens. Convert to lowercase. Also strip leading and
trailing whitespace, dashes, and underscores.
"""
def slugify(value, allow_unicode=False):

    value = str(value)
    value.replace("ä", "ae").replace("Ä", "Ae").replace("ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue").replace("ß", "ss")
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '_', value).strip('-_')

 #  titlestring.replace(" ", "_").replace(",", "_").replace(":", "_").replace("ä", "ae").replace("Ä", "Ae").replace("ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue")
  



source_list = []
source_list.append(source_object("muenchen","sueddeutsche_zeitung", "https://www.sueddeutsche.de", "/thema/Coronavirus_in_M%C3%BCnchen", "a", "sz-teaser"))
source_list.append(source_object("stuttgart","stuttgarter_zeitung", "https://www.stuttgarter-zeitung.de", "https://www.stuttgarter-zeitung.de", "a", "data", "/inhalt." , True ))
source_list.append(source_object("berlin","tagesspiegel","https://m.tagesspiegel.de/","berlin/coronavirus-in-der-hauptstadtregion-neuinfektionen-in-brandenburg-steigen-wieder-zweistellig/25655678.html"))
source_list.append(source_object("potsdam","potsdamer_neuste_nachrichten","https://www.pnn.de/","potsdam/corona-newsblog-fuer-potsdam-und-brandenburg-corona-infektionen-in-brandenburg-wieder-zweistellig/25617916.html"))
source_list.append(source_object("bremen","buten_und_binnen","https://www.butenunbinnen.de/","nachrichten/schwerpunkt-corona-virus-106.html","a", "teaser-link"))
source_list.append(source_object("hamburg","hamburger_abendblatt","https://www.abendblatt.de/","themen/coronavirus/","a", "teaser__content-link"))
#source_list.append(source_object("wiesbaden","stadt","https://www.wiesbaden.de/", "medien/content/Pressemitteilungen.php?category=&search_date=-&search_date_from=" + today + "&search_date_to=" + today + "&search_keywords=corona", "td", "SP-link", "rathausnachrichten", True)) 
source_list.append(source_object("schwerin","svz", "https://www.svz.de/", "lokales/zeitung-fuer-die-landeshauptstadt/", "article", "teaser", "lokales", True)) # alle lokalen nachrichten
source_list.append(source_object("hannover","haz", "https://www.haz.de/", "nachrichten/coronavirus-in-hannover", "a", "pdb-teaser3-teaser-breadcrumb-headline-title-link"))
source_list.append(source_object("duesseldorf","wz", "https://www.wz.de/", "suche/?q=corona&sort=date&ressorts[]=ressort_191145&type=article", "a", "park-teaser__link", "duesseldorf", True))
source_list.append(source_object("magdeburg","kompakt_media", "https://www.kompakt.media/", "coronavirus-magdeburg-aktuell/", "h2", "entry-title"))
source_list.append(source_object("kiel","svz", "https://www.shz.de/", "suche/?q=corona", "article", "teaser", "kiel", True))
source_list.append(source_object("erfurt","tlz", "https://www.tlz.de/", "suche/?q=corona", "article", "teaser", "erfurt", True))
source_list.append(source_object("leipzig","stadt", "https://www.leipzig.de/", "jugend-familie-und-soziales/gesundheit/neuartiges-coronavirus-2019-n-cov/", "div", "news-latest-item"))
source_list.append(source_object("mainz","mainzund", "https://mainzund.de/", "category/wissen-andere-mainzer-geschichten/alles-zur-coronavirus-epidemie-auf-mainzund/", "a", "td-image-wrap"))
source_list.append(source_object("dresden","saechsische", "https://www.saechsische.de/", "search?q=corona+dresden", "div", "article-vbox__img"))

# for source in source_list:
#     jsonstring = json.dumps(source.__dict__)
#         #in datei schreiben
#     with open("article_sources/" + source.city + ".json", "w") as file:
#         for line in jsonstring:
#             file.write(line)

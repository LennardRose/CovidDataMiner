import ssl
import requests
from bs4 import BeautifulSoup
import os
import re
import unicodedata
from source_object import source_object
import json
import datetime
import html5lib


def get_soup_out_of_page(URL):
    
    page = requests.get(URL)
    return BeautifulSoup(page.content, 'html5lib')

"""
collects all tags from the specified URL-combination that fits the html_tag thml_class combination
If no href is found, the children will be searched for a href
"""
def get_articlelink_list(base_URL, path_URL, html_tag, html_class):

    soup = get_soup_out_of_page(base_URL + path_URL)
    articlelist = soup.body.find_all(html_tag, html_class )
    links = []
    for row in articlelist: 
        if row.has_attr('href'):
            links.append(row['href'])
        else:    
            link = search_direct_children_for_href(row)
            if link != None:
                links.append(link)

    return links
    #erster link ist immer der aktuellste, vielleicht speichern und dann abgleichen, dass man nur immer die läd die man noch nicht hat        

"""
searches all children of a tag for a href, returns the first
"""
def search_direct_children_for_href(tag):
    for child in tag.findAll(recursive = True):
        if child.has_attr('href'):
            return child['href']
    else:
        return None



"""
Scrapes only pages that have a match(contition_boolean = True) or have no match(contiditon_boolean = False) of condition in their page_list URLs.
Also checks if the URL is relative or absolute, adds base_URL if necessary
Saves the content of page with the given file_prefix 
"""
def scrape_all_valid_pages(base_URL, page_list, file_prefix, condition, condition_boolean):
    for URL in page_list:
        if is_valid(URL, condition, condition_boolean):
            if is_relative_URL(URL):
                URL = base_URL + URL
            save_content_of_page(URL, file_prefix)    

"""
Scrapes all page_list URLs.
Also checks if the URL is relative or absolute, adds base_URL if necessary
Saves the content of page with the given file_prefix 
"""
def scrape_all_pages(base_URL, page_list, file_prefix):
    for URL in page_list:
        if is_relative_URL(URL):
            URL = base_URL + URL
        save_content_of_page(URL, file_prefix)  

# def save_articles_of_page(base_URL, path_URL, html_tag, html_class):
#     soup = get_soup_out_of_page(base_URL + path_URL)
#     articlelist = soup.body.find_all(html_tag, html_class )



def save_content_of_page(URL, file_prefix, folder = ""):
    print(URL)
    soup = get_soup_out_of_page(URL)
    encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
    text = str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    #metadaten auslesen um namen für file zu bekommen
    for tag in soup.find_all("meta"):
            if tag.get("property", None) == "og:title":
                title = slugify(tag.get("content", None))

    # falls kein titel in meta, guck ob title tag
    if title == None:
        if soup.find_all("title"):
            tag = soup.find_all("title")
            title = slugify(tag)
        # sonst nimm halt timestamp
        else:
            title = slugify(datetime.datetime.now())
        
    

    filename = folder + file_prefix + title + ".txt"

    #in datei schreiben
    with open(filename, "w") as file:
        for line in text:
            file.write(line + os.linesep)

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
    return re.sub(r'[-\s]+', '-', value).strip('-_')

 #  titlestring.replace(" ", "_").replace(",", "_").replace(":", "_").replace("ä", "ae").replace("Ä", "Ae").replace("ö", "oe").replace("Ö", "Oe").replace("ü", "ue").replace("Ü", "Ue")
            

def is_relative_URL(URL):
    return not bool(re.search("^http", URL))


def is_valid(URL, condition, condition_boolean):
    if condition_boolean:
        return bool(re.search(condition, URL))
    else:
        return not bool(re.search(condition, URL))

def scrape(source: source_object):
    # if all articles are on the page
    if source.html_tag == None and source.html_class == None:
        save_content_of_page(source.base_url + source.path_url, source.filename)

    # if the page hase links to all the articles
    else:
        list = get_articlelink_list(source.base_url, source.path_url, source.html_tag, source.html_class)
        
        # if all articles should be scraped
        if source.condition == None:
            scrape_all_pages(source.base_url, list, source.filename)
        
        # if only articles with a spectific URL should be scraped
        else:   
            scrape_all_valid_pages(source.base_url, list, source.filename, source.condition, source.condition_boolean)




if __name__ == '__main__':


    ssl._create_default_https_context = ssl._create_unverified_context
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    source_list = []
    source_list.append(source_object("muenchen_sueddeutsche_zeitung_", "https://www.sueddeutsche.de", "/thema/Coronavirus_in_M%C3%BCnchen", "a", "sz-teaser"))
    source_list.append(source_object("stuttgart_stuttgarter_zeitung_", "https://www.sueddeutsche.de", "https://www.stuttgarter-zeitung.de", "a", "data", "/inhalt." , True ))
    source_list.append(source_object("berlin_tagesspiegel_","https://m.tagesspiegel.de/","berlin/coronavirus-in-der-hauptstadtregion-neuinfektionen-in-brandenburg-steigen-wieder-zweistellig/25655678.html"))
    source_list.append(source_object("potsdam_potsdamer_neuste_nachrichten_","https://www.pnn.de/","potsdam/corona-newsblog-fuer-potsdam-und-brandenburg-corona-infektionen-in-brandenburg-wieder-zweistellig/25617916.html"))
    source_list.append(source_object("bremen_buten_und_binnen_","https://www.butenunbinnen.de/","nachrichten/schwerpunkt-corona-virus-106.html","a", "teaser-link"))
    source_list.append(source_object("hamburg_hamburger_abendblatt_","https://www.abendblatt.de/","themen/coronavirus/","a", "teaser__content-link"))
    source_list.append(source_object("wiesbaden_stadt_","https://www.wiesbaden.de/", "medien/content/Pressemitteilungen.php?category=&search_date=-&search_date_from=" + today + "&search_date_to=" + today + "&search_keywords=corona", "td", "SP-link", "rathausnachrichten", True)) 
    source_list.append(source_object("schwerin_svz_", "https://www.svz.de/", "lokales/zeitung-fuer-die-landeshauptstadt/", "article", "teaser", "lokales", True)) # alle lokalen nachrichten
    source_list.append(source_object("hannover_haz_", "https://www.haz.de/", "nachrichten/coronavirus-in-hannover", "a", "pdb-teaser3-teaser-breadcrumb-headline-title-link"))
    source_list.append(source_object("duesseldorf_wz_", "https://www.wz.de/", "suche/?q=corona&sort=date&ressorts[]=ressort_191145&type=article", "a", "park-teaser__link", "duesseldorf", True))
    source_list.append(source_object("magdeburg_kompakt_media_", "https://www.kompakt.media/", "coronavirus-magdeburg-aktuell/", "h2", "entry-title"))
    source_list.append(source_object("kiel_svz_", "https://www.shz.de/", "suche/?q=corona", "article", "teaser", "kiel", True))
    source_list.append(source_object("erfurt_tlz_", "https://www.tlz.de/", "suche/?q=corona", "article", "teaser", "erfurt", True))
    source_list.append(source_object("leipzig_stadt_", "https://www.leipzig.de/", "jugend-familie-und-soziales/gesundheit/neuartiges-coronavirus-2019-n-cov/", "div", "news-latest-item"))
    source_list.append(source_object("mainz_mainzund_", "https://mainzund.de/", "category/wissen-andere-mainzer-geschichten/alles-zur-coronavirus-epidemie-auf-mainzund/", "a", "td-image-wrap"))
    source_list.append(source_object("dresden_saechsische_", "https://www.saechsische.de/", "search?q=corona+dresden", "div", "article-vbox__img"))

    #for source in source_list:
     #   scrape(source)

    save_content_of_page("https://www.haz.de/Hannover/Aus-der-Stadt/Hannover-Trauergottesdienst-fuer-erstochenen-Dirk-S.-aus-der-Eilenriede", "test")

    
    

    
    

import json
import utils

   

"""
uses the meta tag <meta> in a given soup (Beatifulsoup) to aquire meta information about the article
saves the 
"""
def parse_from_meta_tag(soup, meta_dict):

#metadaten auslesen 
    meta_data = soup.find_all("meta")

    for tag in meta_data:

        if tag.get("property", None) == "og:title":
            meta_dict["title"] = utils.slugify(tag.get("content", None))
            continue

        if meta_dict["description"] == None and ( tag.get("property", None) == "og:description" or tag.get("name", None) == "description" ):
            meta_dict["description"] = tag.get("content", None)
            continue

        if meta_dict["type"] == None and ( tag.get("property", None) == "og:type" or tag.get("name", None) == "type" ):
            meta_dict["type"] = tag.get("content", None)
            continue

        if meta_dict["date"] == None and ( tag.get("name", None) == "DCTERMS.created" or tag.get("name", None) == "date" or tag.get("name", None) == "DC.date.issued" ): 
            meta_dict["date"] = utils.parse_date(tag.get("content", None))
            continue

        if meta_dict["author"] == None and ( tag.get("property", None) == "og:author" or tag.get("name", None) == "author" ): 
            meta_dict["author"] = tag.get("content", None)
            continue

        if meta_dict["keywords"] == None and ( tag.get("property", None) == "og:keywords" or tag.get("name", None) == "keywords" ): 
            meta_dict["keywords"] = tag.get("content", None)
            continue
            
    return meta_dict


"""
uses the <script type=application/ld+json> to retrieve missing meta information
"""
def parse_from_json(soup, meta_dict):

    scripts = json.loads( soup.find('script', {'type':'application/ld+json'}).text.strip() )

    if not scripts:
        return meta_dict

    if meta_dict["date"] == None:
        if scripts["datePublished"]:
            meta_dict["date"] = utils.parse_date(scripts["datePublished"])
        elif scripts["dateCreated"]:
            meta_dict["date"] = utils.parse_date(scripts["dateCreated"])

    if meta_dict["title"] == None:
        if scripts[""]:
            meta_dict["title"] = scripts[""]


def parse_title_from_tag(soup):
    return utils.slugify(soup.find_all("title"))


def parse_metadata(soup, city, site_name, URL):

    # metadaten dictionary initialisieren
    meta_dict = { "title" : None, 
                "description" : None, 
                "url": URL, 
                "type" : None, 
                "date" : None, 
                "city" : city, 
                "site_name" : site_name, 
                "author" : None, 
                "keywords" : None, 
                "filename" : None }

    #metadaten aus meta tags parsen
    meta_dict = parse_from_meta_tag(soup, meta_dict)

    #falls noch werte nicht gefunden, suche aus json ld
    if any([v==None for v in meta_dict.values()]):
        meta_dict = parse_from_json(soup, meta_dict)

    # falls kein titel in meta oder json, guck ob title tag
    if meta_dict["title"] == None:
        meta_dict["title"] = parse_title_from_tag(soup)

    #falls kein datum gefunden, nehme aktuelles datum
    if meta_dict["date"] == None:
        meta_dict["date"] = utils.date_now()

    #setze filename aus komponenten zusammen
    meta_dict["filename"] = city + "_" + site_name + "_" + meta_dict["title"] + ".txt"

    return meta_dict
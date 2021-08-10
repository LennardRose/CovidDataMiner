import ssl
import requests
from bs4 import BeautifulSoup
import os
import re
from source_object import source_object
import json
import datetime
import html5lib
from MetaParser import meta_parser 
import argparse
from ElasticSearchWrapper import ElasticSearchClient
import logging
import sys

def get_soup_out_of_page(URL):
    page = requests.get(URL)
    return BeautifulSoup(page.content, 'html5lib')


def get_articlelink_list(URL, html_tag, html_class):
    """
    collects all tags from the specified URL-combination that fits the html_tag thml_class combination
    If no href is found, the children will be searched for a href
    """

    soup = get_soup_out_of_page(URL)
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


def search_direct_children_for_href(tag):
    """
    searches all children of a tag for a href, returns the first
    """
    for child in tag.findAll(recursive = True):
        if child.has_attr('href'):
            return child['href']
    else:
        return None



def scrape_all_pages(source):
    """
    Scrapes only pages that have no conditions set or 
    a match(contition_boolean = True) or have no match(contiditon_boolean = False) 
    of condition in their page_list URLs.
    Also checks if the URL is relative or absolute, adds base_URL if necessary
    Saves the content of page 
    """
    
    for URL in get_articlelink_list(source["base_url"] + source["path_url"], source["html_tag"], source["html_class"]):
        
        if is_valid(URL, source["condition"], source["condition_boolean"]):

            if is_relative_URL(URL):
                URL = source["base_URL"] + URL

            save_content_of_page(source, URL)    


def is_relative_URL(URL):
    return not bool(re.search("^http", URL))


def is_valid(URL, condition, condition_boolean):
    if condition == None and condition_boolean == None:
        return True
    else:
        if condition_boolean:
            return bool(re.search(condition, URL))
        else:
            return not bool(re.search(condition, URL))


def save_content_of_page(source, URL):
    
    soup = get_soup_out_of_page(URL)
    encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
    text = str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    parser = meta_parser( URL, soup, source)
    meta_data = parser.parse_metadata() #das URL ist von der individuellen seite, nicht aus Base + Path, ausser bei direktem scrapen der seite

    #in datei schreiben
    with open("./articles/" + meta_data["filename"], "w") as file:
        for line in text:
            file.write(line + os.linesep)

    es_client.index_meta_data(meta_data)  


def scrape(source):

    # if all articles are on the page
    if source["html_tag"] == None and source["html_class"] == None:
        save_content_of_page(source, source["base_url"] + source["path_url"])

    # if the page has links to all the articles
    else:
        scrape_all_pages(source)
        

def parse_arguments():

    parser = argparse.ArgumentParser(description='scrapes sources by the configs given')

    parser.add_argument("-e", "--elasticsearch", action="append", dest="elastic_ids", default=[],
                        help="config stored in elasticsearch, add id of the config")

    parser.add_argument("-f", "--file", action="append", dest="filenames", default=[],
                        help="config stored in file, add filename")

    return parser.parse_args()

def parse_data_from_arguments():

    args = parse_arguments()
    data = []
    print(args)

    if len(sys.argv) < 2: #programmname ist auch ein argument, deshalb 2 ---> scrape alle in elasticsearch wenn nichts weiter angegeben
        data = es_client.get_all_article_configs()

    for filename in args.filenames:
        with open(filename, "r") as file:
            data.append(json.load(file))
            
    for id in args.elastic_ids:
        data.append(es_client.get_article_config(id))

    return data

if __name__ == '__main__':

    logging.info("start scraping")
    ssl._create_default_https_context = ssl._create_unverified_context
    
    es_client = ElasticSearchClient()

    data = parse_data_from_arguments()

    for source in data:
            scrape(source)





    
    

    
    

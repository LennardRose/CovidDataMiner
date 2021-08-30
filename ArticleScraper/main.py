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
from Config import STANDARD_FORMAT 

def get_soup_out_of_page(URL):
    """
    :param URL: the url to get the soup (Beatifulsoup) of
    :return: the soup, parsed with 'html5lib' parser
    """
    page = requests.get(URL)
    return BeautifulSoup(page.content, 'html5lib')


def get_articlelink_list(URL, html_tag, html_class):
    """
    collects all tags from the specified URL-combination that fits the html_tag html_class combination
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
    creates a list with the links to all articles from the given source configuration
    saves the content of every valid link in the list
    also completes every relative URL with the base_url if necessary
    """
    
    for URL in get_articlelink_list(source["base_url"] + source["path_url"], source["html_tag"], source["html_class"]):
        
        if is_valid(URL, source["condition"], source["include_condition"]):

            if is_relative_URL(URL):
                URL = source["base_URL"] + URL

            save_content_of_page(source, URL)    


def is_relative_URL(URL):
    """
    checks if the given URL starts with http, to determine if it is a relative URL
    lots of webpages return only the path url on their own website
    :param URL: the URL to check
    :return: false if URL starts with http, otherwise true
    """
    return not bool(re.search("^http", URL))


def is_valid(URL, condition, include_condition):
    """
    checks if the given URL matches the given condition, returns wether the url should be included in the list based on the include_condition value
    necessary because a lot of websites got fake articles with ads or have their interesting articles under a similar url path, 
    one condition which can be set to in/exclude was powerful enough, maybe changed in the future with a funciton that wraps this function
    :param URL: the url to check
    :param condition: the string to match in the url
    :param include_condition: true if matches of the url should be included, false if matches should be excluded
    :return: true if url includes condition NXOR include_condition set true, else false 
    """
    if condition == None and include_condition == None:
        return True
    else:
        if include_condition:
            return bool(re.search(condition, URL))
        else:
            return not bool(re.search(condition, URL))


def save_content_of_page(source, URL):
    """
    saves the html source of the given URL 
    also saves the meta data of the page as configurated in the given article source
    """
    
    soup = get_soup_out_of_page(URL)
    encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
    text = str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    parser = meta_parser( URL, soup, source)
    parser.parse_metadata() #das URL ist von der individuellen seite, nicht aus Base + Path, ausser bei direktem scrapen der seite
    meta_data = parser.get_meta_data()

    #in datei schreiben
    with open("./articles/" + meta_data["filename"], "w") as file:
        for line in text:
            file.write(line + os.linesep)

    es_client.index_meta_data(meta_data)  


def scrape(source):
    """
    scrapes the page in the given source, based on if it is a article on a single page to scrape or if it is 
    a page with links to the articles 
    """

    # if all articles are on the page
    if source["html_tag"] == None and source["html_class"] == None:
        save_content_of_page(source, source["base_url"] + source["path_url"])

    # if the page has links to all the articles
    else:
        scrape_all_pages(source)
        

def parse_arguments():
    """
    parses the arguments
    """

    parser = argparse.ArgumentParser(description='scrapes sources by the configs given')

    parser.add_argument("-e", "--elasticsearch", action="append", dest="elastic_ids", default=[],
                        help="config stored in elasticsearch, add id of the config")

    parser.add_argument("-f", "--file", action="append", dest="filenames", default=[],
                        help="config stored in file, add filename")

    return parser.parse_args()

def parse_data_from_arguments():
    """
    retrieves the source configurations mentioned in the arguments
    :return: all found data
    """

    args = parse_arguments()
    data = []

    if len(sys.argv) < 2: #programmname ist auch ein argument, deshalb 2 ---> scrape alle in elasticsearch wenn nichts weiter angegeben
        data = es_client.get_all_article_configs()

    for filename in args.filenames:
        try:
            with open(filename, "r") as file:
                data.append(json.load(file))
        except:
            logging.error(filename + " not found.")
            
    for id in args.elastic_ids:
        data.append(es_client.get_article_config(id))

    return data

if __name__ == '__main__':

    logging.basicConfig(format='[%(levelname)s][%(asctime)s]: %(message)s', datefmt = STANDARD_FORMAT, level=logging.DEBUG)
    logging.info("Start Scraper")
    ssl._create_default_https_context = ssl._create_unverified_context
    
    es_client = ElasticSearchClient()

    data = parse_data_from_arguments()

    for source in data:
            logging.info("Start scraping from source URL: " + source["base_url"] + source["path_url"])
            scrape(source)

    logging.info("Close Scraper")





    
    

    
    

import ssl
import requests
from bs4 import BeautifulSoup
import os
import re
from source_object import source_object
import json
import datetime
import html5lib
import meta_parser
import argparse
from ElasticSearchWrapper import ElasticSearchClient
import logging

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
def scrape_all_valid_pages(base_URL, page_list, city, site_name, condition, condition_boolean):
    for URL in page_list:
        if is_valid(URL, condition, condition_boolean):
            if is_relative_URL(URL):
                URL = base_URL + URL
            save_content_of_page(URL, city, site_name)    

"""
Scrapes all page_list URLs.
Also checks if the URL is relative or absolute, adds base_URL if necessary
Saves the content of page with the given file_prefix 
"""
def scrape_all_pages(base_URL, page_list, city, site_name):
    for URL in page_list:
        if is_relative_URL(URL):
            URL = base_URL + URL
        save_content_of_page(URL, city, site_name)  

# def save_articles_of_page(base_URL, path_URL, html_tag, html_class):
#     soup = get_soup_out_of_page(base_URL + path_URL)
#     articlelist = soup.body.find_all(html_tag, html_class )



def save_content_of_page(URL, city, site_name):
    

    soup = get_soup_out_of_page(URL)
    encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
    text = str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    meta_data = meta_parser.parse_metadata(soup, city, site_name, URL)

    #in datei schreiben
    with open(meta_data["filename"], "w") as file:
        for line in text:
            file.write(line + os.linesep)

    #print(meta_dict) # an dieser stelle dann über ES client den ganzen kram in die unendlichkeit feuern
       

def is_relative_URL(URL):
    return not bool(re.search("^http", URL))


def is_valid(URL, condition, condition_boolean):
    if condition_boolean:
        return bool(re.search(condition, URL))
    else:
        return not bool(re.search(condition, URL))

def scrape(source):
    # if all articles are on the page
    if source.html_tag == None and source.html_class == None:
        save_content_of_page(source.base_url + source.path_url, source.city, source.site_name)

    # if the page has links to all the articles
    else:
        list = get_articlelink_list(source.base_url, source.path_url, source.html_tag, source.html_class)
        
        # if all articles should be scraped
        if source.condition == None:
            scrape_all_pages(source.base_url, list, source.city, source.site_name)
        
        # if only articles with a spectific URL should be scraped
        else:   
            scrape_all_valid_pages(source.base_url, list, source.city, source.site_name, source.condition, source.condition_boolean)


def parse_arguments():

    parser = argparse.ArgumentParser(description='scrapes sources by the configs given')

    parser.add_argument("-e", "--elasticsearch", action="append", dest="elastic_ids", default=[],
                        help="config stored in elasticsearch, add id of the config")

    parser.add_argument("-f", "--file", action="append", dest="filenames", default=[],
                        help="config stored in file, add filename")

    return parser.parse_args()

def parse_input_arguments():

    args = parse_arguments()
    data = []

    for filename in args.filenames:
        with open(filename, "r") as file:
            data.append(json.load(file))
            
    for id in args.elastic_ids:
        data.append(es_client.search_article_config(id))

    return data

if __name__ == '__main__':

    logging.info("start scraping")
    ssl._create_default_https_context = ssl._create_unverified_context
    es_client = ElasticSearchClient()

    data = parse_input_arguments()

    for source in data:
        scrape(source)



    #today = datetime.datetime.now().strftime("%d.%m.%Y")



    
    

    
    

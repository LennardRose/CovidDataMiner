import utils
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
import re
import html5lib
from meta_parser import meta_parser
import client_factory
import logging
import ssl
import os

class ArticleScraper:

    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        self.driver = self.get_webdriver()

    def get_webdriver(self):
        """
        returns a webdriver for selenium
        https://www.makeuseof.com/how-to-install-selenium-webdriver-on-any-computer-with-python/
        """
        try:
            driver_options = Options()
            driver_options.headless = True
            path = os.path.join(utils.config["WEBDRIVER_DIR"], utils.config["WEBDRIVER_FILE"])
            return webdriver.Chrome(executable_path=path, options=driver_options)
        except:
            logging.error("failed to initialize webdriver for selenium, make sure you downloaded a driver and wrote the correct path to config")


    def get_text_of_page(self, soup):
        """
        parse soup to string 
        takes care of proper encoding
        """
        encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
        return str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    def get_soup_of_static_page(self, URL):
        """
        extract content of static loaded page
        :param URL: the url to get the soup (Beatifulsoup) of
        :return: the soup, parsed with 'html5lib' parser
        """
        page = requests.get(URL)
        return BeautifulSoup(page.content, 'html5lib')

    def get_soup_of_dynamic_page(self, URL):
        """
        extract content of dynamic loaded page
        :param URL: the url to get the soup (Beatifulsoup) of
        :return: the soup, parsed with 'html5lib' parser
        """
        try:
            self.driver.get(URL)
            time.sleep(1) #load page
            return BeautifulSoup(self.driver.page_source, 'html5lib')
        except:
            logging.warning("something went wrong while trying to load dynamic page with selenium")



    def get_articlelink_list(self, URL, html_tag, html_class):
        """
        collects all tags from the specified URL-combination that fits the html_tag html_class combination
        If no href is found, the children will be searched for a href
        """

        #first try static page
        soup = self.get_soup_of_static_page(URL)
        article_link_list = soup.body.find_all(html_tag, html_class )
        links = []

        #if static doesnt work try dynamic
        if article_link_list == [] or article_link_list == None:
            soup = self.get_soup_of_dynamic_page(URL)
            article_link_list = soup.body.find_all(html_tag, html_class )
            

        # if still no result something must be wrong with the html_tag and html_class
        if article_link_list == [] or article_link_list == None:
            logging.error("No results found for: " + html_class + " and " + html_tag)

        for article_link in article_link_list: 

            if article_link.has_attr('href'):
                links.append(article_link['href'])

            else:    
                link = self.search_direct_children_for_href(article_link)

                if link != None:
                    links.append(link)

        links.reverse() # important to have the newest article at the last index of the list, so it has the newest indexing time, making it easier (if not possible) to search for without having to write an overcomplicated algorithm

        return links



    def search_direct_children_for_href(self, tag):
        """
        searches all children of a tag for a href, returns the first
        """
        for child in tag.findAll(recursive = True):
            if child.has_attr('href'):
                return child['href']
        else:
            return None



    def scrape_all_pages(self, source):
        """
        creates a list with the links to all articles from the given source configuration
        saves the content of every valid link in the list
        also completes every relative URL with the base_url if necessary
        """
        source_URL = source["base_url"] + source["path_url"]
        most_recent_saved_articles_url = client_factory.get_meta_client().get_latest_entry_URL(source_URL, source["region"]) 


        for URL in self.get_articlelink_list(source_URL, source["html_tag"], source["html_class"]):
            
            if self.is_valid(URL, source["url_conditions"]):

                if self.is_relative_URL(URL):
                    URL = source["base_url"] + URL

                if not self.was_already_saved(most_recent_saved_articles_url, URL):
                    self.save_content_of_page(source, URL)


    def was_already_saved(self, most_recent_saved_articles_url, URL):# a lot of text for a function that does nothing else than comparing two strings, but easy to break things here
        """
        the first link in the article_list is always the most recent
        by iterating these and break if the url is matching the url of the latest meta_data document we are preventing the system of scraping already present data
        :param most_recent_saved_articles_url: the URL of the most recent saved article (in an earlier call)
        :param URL: the url of the current link
        :return: true if the URL matches the url of the most recent url
        """
        if most_recent_saved_articles_url:
            return URL in most_recent_saved_articles_url
        else:
            return False



    def is_relative_URL(self, URL):
        """
        checks if the given URL starts with http, to determine if it is a relative URL
        lots of webpages return only the path url on their own website
        :param URL: the URL to check
        :return: false if URL starts with http, otherwise true
        """
        return not bool(re.search("^http", URL))


    def is_valid(self,URL, conditions):
        """
        checks if the given URL matches the given condition, returns wether the url should be included in the list based on the include_condition value
        necessary because a lot of websites got fake articles with ads or have their interesting articles under a similar url path, 
        one condition which can be set to in/exclude was powerful enough, maybe changed in the future with a funciton that wraps this function
        :param URL: the url to check
        :param condition: the string to match in the url
        :param include_condition: true if matches of the url should be included, false if matches should be excluded
        :return: true if url includes condition NXOR include_condition set true, else false 
        """
        valid = True

        if conditions != None and conditions != []:

            for condition in conditions:

                is_included = bool(re.search(condition["condition_string"], URL)) #if the condition_string is part of the URL

                if condition["include_condition"]: #if the condition_string should be included in the URL
                    if is_included: 
                        valid = valid
                    else:
                        valid = False
                        
                else: # if the condition_string should not be included in the URL
                    if is_included:
                        valid = False
                    else:
                        valid = valid

        return valid


    def save_content_of_page(self,source, URL):
        """
        saves the html source of the given URL 
        also saves the meta data of the page as configurated in the given article source
        """
        logging.info("Save content of: " + URL)
        soup = self.get_soup_of_static_page(URL)

        parser = meta_parser( URL, soup, source)
        parser.parse_metadata() #das URL ist von der individuellen seite, nicht aus Base + Path, ausser bei direktem scrapen der seite
        meta_data = parser.get_meta_data()

        client_factory.get_meta_client().index_meta_data(meta_data)  

        text = self.get_text_of_page(soup)
        path = os.path.join("articles", source["region"], source["site_name"], utils.date_today())
        client_factory.get_file_client().save_as_file(path, meta_data["filename"], text)


    def scrape(self, source):
        """
        scrapes the page in the given source, based on if it is a article on a single page to scrape or if it is 
        a page with links to the articles 
        """

        logging.info("Start scraping from source URL: " + source["base_url"] + source["path_url"])

        # if all articles are on the page
        if source["html_tag"] == None and source["html_class"] == None:
            self.save_content_of_page(source, source["base_url"] + source["path_url"])

        # if the page has links to all the articles
        else:
            self.scrape_all_pages(source)
            
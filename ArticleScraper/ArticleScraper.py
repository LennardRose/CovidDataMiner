
import requests
from bs4 import BeautifulSoup
import re
import html5lib
from MetaParser import meta_parser 
from Repository import Repository
import logging
import ssl

class ArticleScraper:

    def __init__(self):
        self.repository = Repository()
        ssl._create_default_https_context = ssl._create_unverified_context


    def get_text_of_page(self, soup):
        """
        parse soup to string 
        takes care of proper encoding
        """
        encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
        return str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    def get_soup_out_of_page(self, URL):
        """
        :param URL: the url to get the soup (Beatifulsoup) of
        :return: the soup, parsed with 'html5lib' parser
        """
        page = requests.get(URL)
        return BeautifulSoup(page.content, 'html5lib')



    def get_articlelink_list(self, URL, html_tag, html_class):
        """
        collects all tags from the specified URL-combination that fits the html_tag html_class combination
        If no href is found, the children will be searched for a href
        """
        most_recent_saved_articles_url = self.repository.get_latest_entry_URL(URL) 

        soup = self.get_soup_out_of_page(URL)
        article_link_list = soup.body.find_all(html_tag, html_class )
        links = []
        result_list = []

        for article_link in article_link_list: 

            if article_link.has_attr('href'):
                links.append(article_link['href'])

            else:    
                link = self.search_direct_children_for_href(article_link)

                if link != None:
                    links.append(link)

        for link in links:

            if self.was_already_saved(most_recent_saved_articles_url, link):
                logging.info("Reached last element of previous session: " + link)
                break
            else:
                result_list.insert(0, link) # filling the resultlist so it is a reverse list of the links with the first element being the first article after the most recent saved one

        return result_list  # important to have the newest article at the last index of the list, so it has the newest indexing time, making it easier (if not possible) to search for without having to write an overcomplicated algorithm


        #erster link ist immer der aktuellste, vielleicht speichern und dann abgleichen, dass man nur immer die läd die man noch nicht hat        


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
        
        for URL in self.get_articlelink_list(source_URL, source["html_tag"], source["html_class"]):
            
            if self.is_valid(URL, source["condition"], source["include_condition"]):

                if self.is_relative_URL(URL):
                    URL = source["base_URL"] + URL

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
            return most_recent_saved_articles_url == URL
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


    def is_valid(self,URL, condition, include_condition):
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


    def save_content_of_page(self,source, URL):
        """
        saves the html source of the given URL 
        also saves the meta data of the page as configurated in the given article source
        """
        logging.info("Save content of: " + URL)
        soup = self.get_soup_out_of_page(URL)

        parser = meta_parser( URL, soup, source)
        parser.parse_metadata() #das URL ist von der individuellen seite, nicht aus Base + Path, ausser bei direktem scrapen der seite
        meta_data = parser.get_meta_data()
        self.repository.index_meta_data(meta_data)  

        text = self.get_text_of_page(soup)
        self.repository.save_as_file(meta_data["filename"], text)


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
            
import re
from selenium import webdriver
import pandas
import time
from selenium.webdriver.firefox.options import Options
import json


class Webscraper:

    def __init__(self):
        self.driver = self._get_headless_firefox_webdriver()

    # das hier braucht nen installierten firefox webdriver
    def _get_headless_firefox_webdriver(self):
        options = Options()
        options.headless = True
        return webdriver.Firefox(options=options)

    def _extract_something_from_html(self, page):
        string = re.search('hier könnte ihr regex stehen', page)
        return int(re.search("hier auch", string.group(0)).group())

    #         vielleicht für später
    #         page = driver.page_source
    #         print(page)
    #         jsonfile = driver.find_element_by_id('json').text
    #         alljson = json.loads(str(jsonfile))
    #         return int(alljson['parent']['child1']['child2']['child3'])

    def get_stuff_from_site(self, URL):
        # 2 mal laden um die cookies zu laden, Stack Overflow sagt so
        self.driver.get(URL)
        self.driver.add_cookie({'name': 'hier cookie name', 'value': 'und der wert'})
        self.driver.get(URL)
        return self._extract_something_from_html(str(self.driver.page_source))

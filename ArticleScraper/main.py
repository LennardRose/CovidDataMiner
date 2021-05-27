import requests
from bs4 import BeautifulSoup
from lxml import html
import ssl
import os


def get_soup_out_of_page(URL):
    
    page = requests.get(URL)
    return BeautifulSoup(page.content, 'html.parser')

def get_articlelink_list(URL):

    soup = get_soup_out_of_page(URL)
    articlelist = soup.body.find_all('a', class_="sz-teaser" )#<--CSS selector um auf die liste zuzugreifen 
    links = []
    for row in articlelist: #brauch ne mapfunktion, beautifulsoup hat keine doku 
        if row:
            links.append(row['href'])
    return links
    #erster link ist immer der aktuellste, vielleicht speichern und dann abgleichen, dass man nur immer die läd die man noch nicht hat        

def get_content_of_page(URL):

    soup = get_soup_out_of_page(URL)
    encoding = soup.original_encoding or 'utf-8' #encoding für sonderzeichen sonst heult er rum
    text = str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    #metadaten auslesen um namen für file zu bekommen, besser dann das datum des tages an dem gescraped wurde einfügen
    for tag in soup.find_all("meta"):
        if tag.get("name", None) == "last-modified":
            date = str(tag.get("content", None)).replace(" ", "_").replace(",", "_").replace(":", "_")

    filename = "Muenchen_SueddeutscheZeitung_" + date + ".txt"

    #in datei schreiben
    with open(filename, "w") as file:
        for line in text:
            file.write(line + os.linesep)


if __name__ == '__main__':

    ssl._create_default_https_context = ssl._create_unverified_context
    URL = "https://www.sueddeutsche.de/thema/Coronavirus_in_M%C3%BCnchen"   

    print(get_articlelink_list(URL))
    

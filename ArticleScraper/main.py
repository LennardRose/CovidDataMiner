import requests
import re
from bs4 import BeautifulSoup
import urllib
from datetime import datetime
import ssl
import os


ssl._create_default_https_context = ssl._create_unverified_context
URL = "https://www.sueddeutsche.de/thema/Coronavirus_in_M%C3%BCnchen"

if __name__ == '__main__':
    #seite holen
    page = requests.get(URL)

    #seite aufbereiten
    soup = BeautifulSoup(page.content, 'html.parser')
    encoding = soup.original_encoding or 'utf-8'
    text = str(soup.encode(encoding)).split("\\n") #er checkt einfach nicht dass das hier lineseperators sind

    #metadaten auslesen um namen für file zu bekommen
    for tag in soup.find_all("meta"):
        if tag.get("name", None) == "last-modified":
            date = str(tag.get("content", None)).replace(" ", "_").replace(",", "_").replace(":", "_")

    filename = "Muenchen_SueddeutscheZeitung_" + date + ".txt"

    #in datei schreiben
    with open(filename, "w") as file:
        for line in text:
            file.write(line + os.linesep)


            #next steps: das ist der content der übersichtsseite, die artikel sind unter /html/body/div[3]/div/div/div[1]/div[4]/div[1]/div[1]/a bzw. html.__ninja_cookie_safari body.muenchen.global div#sueddeutsche.site div#wrapperbelt.site__wrapper div#wrapper.site__wrapper__content div.sz-page.sz-clearfix div.mainpage.theme.sz-page__main-column div.teaserlist div.sz-teaserlist-element a.sz-teaser
            #den dann auslesen bzw. die href links speichern und dann alle verlinkten artikel auslesen

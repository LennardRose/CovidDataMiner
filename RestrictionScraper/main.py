import requests
import re
from bs4 import BeautifulSoup
import urllib
from datetime import datetime
import ssl


ssl._create_default_https_context = ssl._create_unverified_context
URL = "https://www.stmgp.bayern.de/coronavirus/"

def getImgURLfromElem(elem):
    if "Regel" in elem['alt']:
        srcSet = elem['srcset']
        srcSet = srcSet.split(',')

        srcSet = ['http' + re.search('http(.*).png', str).group(1) + '.png' for str in srcSet]
        # brauchen wir alle Links zu den Bildern?
        # hol mir jetzt mal nur das größte Bild weil geile Auflösung
        size = len(srcSet)
        imgURL = srcSet[size - 1]
        return imgURL

if __name__ == '__main__':
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    img_elems = soup.find_all('img', class_='teaser-image bg-src')
    imgURLs = [getImgURLfromElem(elem) for elem in img_elems]
    imgURLs = [ elem for elem in imgURLs if elem is not None]
    index = 0
    for each in imgURLs:
        index += 1
        fileName = datetime.now().strftime("%d-%m-%Y_%H-%M-%S_") + "bayern_" + str(index) + ".png"
        urllib.request.urlretrieve(each, fileName )

import requests
import re
from bs4 import BeautifulSoup
import urllib
from pdf2image import convert_from_path

import ocrmypdf
import pytesseract
try:
    from PIL import Image
except ImportError:
    import Image
from datetime import datetime
import ssl

#pytesseract.pytesseract.tesseract_cmd = 'D:/Programme/Tesseract/tesseract'
# plan for the scraper:
# future config will tell what exactly to scrape and what type
# scrape from every landesregierungs website
# if picture -> put into tesseract
# if pdf -> put into ocrmypdf // klappt wohl nicht -> https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/
# search text from picture or pdf
# put into json locally first

ssl._create_default_https_context = ssl._create_unverified_context
URL = "https://www.stmgp.bayern.de/coronavirus/"

def getImgURLfromElem(elem):
    if "Regeln" in elem['alt']:
        srcSet = elem['srcset']
        srcSet = srcSet.split(',')

        srcSet = ['http' + re.search('http(.*).png', str).group(1) + '.png' for str in srcSet]
        srcSet.sort()
        # brauchen wir alle Links zu den Bildern?
        # hol mir jetzt mal nur das größte Bild weil geile Auflösung
        size = len(srcSet)
        imgURL = srcSet[size - 1]
        return imgURL

def generateTxtFileFromPDF(pdfFile):
    pages = convert_from_path(pdfFile, 500)
    image_counter = 1
    for page in pages:
        filename = "page_" + str(image_counter) + ".jpg"
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1
    filelimit = image_counter - 1
    outfile = "out_text.txt"
    f = open(outfile, "a")
    for i in range(1, filelimit + 1):
        filename = "page_" + str(i) + ".jpg"
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        f.write(text)
    f.close()

if __name__ == '__main__':
    pdfFile = '210513_auf_einen_Blick.pdf'

    #print(pytesseract.image_to_string(Image.open('28-05-2021_12-39-52_bayern_u50.png')))
    #print(pytesseract.image_to_string('28-05-2021_12-39-52_bayern_u50.png'))
    #ocrmypdf.ocr("210513_auf_einen_Blick.pdf", "output.pdf", deskew=True)

    exit(0)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    img_elems = soup.find_all('img')
    imgURLs = [getImgURLfromElem(elem) for elem in img_elems]
    imgURLs = [ elem for elem in imgURLs if elem is not None]
    index = 0
    fileNames = [""] * len(imgURLs)
    for each in imgURLs:
        incidenceType = re.search('ueberblick_(.*).png', each).group(1)
        fileNames[index] = datetime.now().strftime("%d-%m-%Y_%H-%M-%S_") + "bayern_" + incidenceType + ".png"
        urllib.request.urlretrieve(each, fileNames[index])
        index += 1
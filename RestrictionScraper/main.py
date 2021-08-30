import requests
import re
import urllib
import ssl
import datefinder
import locale
import html5lib
import json
import os.path
from pdf2image import convert_from_path
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from elasticsearch import Elasticsearch
import pytesseract
import pandas as pd
import pdfminer
import pdfminer.high_level
from selenium import webdriver
from bs4.element import Comment
#from pywebcopy import save_webpage

try:
    from PIL import Image
except ImportError:
    import Image

# pytesseract.pytesseract.tesseract_cmd = 'D:/Programme/Tesseract/tesseract'
# plan for the scraper:
# future config will tell what exactly to scrape and what type
# scrape from every landesregierungs website
# if picture -> put into tesseract
# if pdf -> put into ocrmypdf // klappt wohl nicht -> https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/
# search text from picture or pdf
# put into json locally first

logging.basicConfig(level=logging.INFO)
ssl._create_default_https_context = ssl._create_unverified_context
#URL = "https://www.stmgp.bayern.de/coronavirus/"
# https://regex101.com/r/2BXdcV/1 -> vll https://regex101.com/r/TyQzsm/1
DATE_REGEX = r"([1-3]?[0-9][.]([ ](Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([ ]202[0-9])?|[0-1]?[0-9][.]?(202[0-9])?))\D"
OTHER_DATE_REGEX = r"(ab |vom |, |Stand(:)? |am ){1}[1-3]?[0-9][.]([ ](Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([ ]202[0-9])?|(0|1)?[0-9][.]?(202[0-9])?) "
# https://regex101.com/r/4J8BJ9/1
INCIDENCE_REGEX = r"(?<=Inzidenzstufe \d \n[(]).*(?=\))"
# https://regex101.com/r/FojuZ9/1
OTHER_INCIDENCE_REGEX = r"(((?<=Inzidenzstufe)|(?<=Inzidenzwert)|(?<=Inzidenz)|(?<=Schwellenwert))).{0,20}(\d{2,3})"

attributes = ["validFrom", "incidenceBased", "federateState", "creationDate", "incidenceRanges", "tags"]
#tags = ["Maskenpflicht", "Kontaktbeschrankung", "Veranstaltungen", "Kultur", "Gastronomie", "Schule", "Sport"]
tags = {
    "Maskenpflicht" : ["Maskenpflicht"],
    "Kontaktbeschränkung" : ["Kontaktbeschränkung", "Kontaktbeschrankung"],
    "Veranstaltungen" : ["Events", "Veranstaltungen"],
    "Kultur" : ["Kultur"],
    "Gastronomie" : ["Gastronomie"],
    "Schule" : ["Schule", "Kindergarten"],
    "Sport" : ["Sport", "Fitnessstudios"]
}

def fixURL(url, addon):
    index = re.search("(?<=[a-zA-Z])/{1}", row.URL).start()
    if not url.startswith(row.URL[:index]):
        url = row.URL[:index] + addon
    return url

def getImgURLfromElem(elem):
    if "Regeln" in elem['alt'] or "Regelung" in elem['alt'] or not elem['alt'] or "Änderung" in elem['alt']:
        imgURL = elem['src']

        imgURL = fixURL(imgURL, elem['src'])

        logging.info("Filtering found Img-Element %s", imgURL)
        return imgURL

    return None

def getPDFURLfromElem(elem):

    pdfURL = elem["href"]

    pdfURL = fixURL(pdfURL, elem["href"])

    logging.info("Filtering found PDF %s", pdfURL)
    return pdfURL

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

def savePage(URL, directory):

    if not os.path.isdir(directory):
        os.makedirs(directory)

    response = urllib.request.urlopen(URL)
    webContent = response.read()
    fileName = directory + "page.html"

    #kwargs = {'bypass_robots': True, 'project_name': 'recognisable-name'}
    #save_webpage(URL, directory, **kwargs)

    open(fileName, 'wb').write(webContent)


def saveImagesFromPage(imgURLs, directory):

    #fileNames = [""] * len(imgURLs)
    txtData = ""

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for index, imgURL in enumerate(imgURLs, start=0):

        #clean url
        if not imgURL.find('?') < 1:
            imgURL = imgURL[:imgURL.find('?')]

        t, dataType = os.path.splitext(imgURL)

        image = 'image' + str(index+1)
        fileName = directory+image+dataType
        fileNameBG = directory + image + "BG" + dataType
        fileNameBW = directory + image + "BW" + dataType

        #TODO: save raw data to hadoop

        logging.info("downloading File %s", fileName)
        urllib.request.urlretrieve(imgURL, fileName)

        logging.info("converting %s into B&G",fileName)
        imgBG = Image.open(fileName).convert("L")
        imgBW = Image.open(fileName).convert("1", dither=Image.NONE)

        imgBG.save(fileNameBG)
        imgBW.save(fileNameBW)

        logging.info("extracting text from image")
        #data = pytesseract.image_to_string(Image.open(fileNames[index]), lang='deu')
        data = pytesseract.image_to_string(imgBW, lang='deu')

        #with open(fileNames[index] + ".txt", "w") as text_file:
        #   text_file.write(data)

        txtData += '\n' + data

    return txtData

def savePDFfromPage(pdfURLs, directory):

    fileNames = [""] * len(pdfURLs)
    txtData = ""

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for index, pdfURL in enumerate(pdfURLs, start=0):

        fileName = directory + pdfURL[pdfURL.rindex("/")+1:pdfURL.rindex(".")] + ".pdf"
        logging.info("downloading File %s", fileName)
        urllib.request.urlretrieve(pdfURL, fileName)

        with open(fileName, 'rb') as fin:
            data = pdfminer.high_level.extract_text(fin, codec='utf-8')
            #data = data.encode('utf-8').decode("utf-8")

        with open(fileName + ".txt", "w", encoding='utf-8') as text_file:
            text_file.write(data)

        txtData += '\n' + data

    return txtData

def extractIncidences(data):

    incidenceRanges = []

    matches = re.finditer(OTHER_INCIDENCE_REGEX, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        if not match.group(3) in incidenceRanges:
            incidenceRanges.append(match.group(3))
        #print(match.group(3))

    incidenceRanges.sort()

    return incidenceRanges

def extractDate(data):
    match = re.search(OTHER_DATE_REGEX, data, re.IGNORECASE)
    if not match:
        match = re.search(DATE_REGEX, data, re.IGNORECASE)
    if match:
        beginDateStr = match.group()
        #beginDateStr = beginDateStr[:-1]
        beginDateStr = beginDateStr.rstrip()

        # date has chars infront
        if re.search(r"\d", beginDateStr).start() > 0:
            index = re.search(r"\d", beginDateStr).start()
            beginDateStr = beginDateStr[index:]

        # date has chars behind
        if re.search(r"[^a-zA-Z0-9]*$",beginDateStr).start() > 0:
            # regex to find Any character that is NOT a letter or number
            index = re.search(r"[^a-zA-Z0-9]*$",beginDateStr).start()
            beginDateStr = beginDateStr[:index]

        if any(c.isalpha() for c in beginDateStr) and not beginDateStr[-1].isnumeric():
            now = datetime.now()
            beginDateStr += " " + str(now.year)
        locale.setlocale(locale.LC_ALL, "german")
        try:
            return datetime.strptime(beginDateStr, '%d. %B %Y')
        except:
            try:
                return datetime.strptime(beginDateStr, '%d.%m.%Y')
            except:
                logging.error("date conversion failed")
    logging.error("No ValidFrom Date found...")
    return None

def checkForTags(restrictionData, data, tags):
    for tag, keys in tags.items():
        for key in keys:
            if re.search(key, data, re.IGNORECASE):
            #if any(key in data for key in keys): #if any string from the list of keys is in data
                if restrictionData['tags'] is None:
                    restrictionData['tags'] = [tag]
                else:
                    if tag not in restrictionData['tags']:
                        restrictionData['tags'].append(tag)
            else:
                continue

def getInformationFromPDF(txtData):
    if txtData:
        for index, pdfFile in enumerate(pdfFiles, start=0):
            logging.info("analyzing Metadata for file %s", pdfFile)



            if index == 0:
                restrictionData['validFrom'] = extractDate(data).strftime("%d-%m-%Y")

            # get incidence ranges
            matches = re.finditer(INCIDENCE_REGEX, data, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                if match.group().startswith("unter"):
                    incidenceStep = "<"+match.group()[-2:]
                elif match.group()[0].isnumeric():
                    incidenceStep = match.group()[:2] + "-" + match.group()[-2:]
                elif "ber" in match.group():
                    incidenceStep = ">"+match.group()[-2:]


                if restrictionData["incidenceSteps"] is None:
                    restrictionData["incidenceSteps"] = [incidenceStep]
                else:
                    if incidenceStep not in restrictionData["incidenceSteps"]:
                        restrictionData["incidenceSteps"].append(incidenceStep)


            checkForTags(restrictionData, data, tags)


def getInformationFromData(txtData, restrictionData):

    if txtData:
        #for index, imgFile in enumerate(imgFiles, start=0):

        logging.info("analyzing Metadata...")

        restrictionData['validFrom'] = extractDate(txtData).strftime("%d-%m-%Y")

        incidenceRanges = extractIncidences(txtData)

        if incidenceRanges:
            restrictionData["incidenceRanges"] = incidenceRanges
            restrictionData["incidenceBased"] = True

        checkForTags(restrictionData, txtData, tags)

def saveMetadata(es, restrictionData):
    # send metadata to elastic search
    fileName = directory+"data.json"
    with open(fileName, 'w') as outfile:
        logging.info("writing Metadata-JSON to File %s", fileName)
        json.dump(restrictionData, outfile)

    logging.info("writing Metadata-JSON to Elasticsearch")
    json_object = json.dumps(restrictionData)

    uid = restrictionData["federateState"] + restrictionData['validFrom']

    if not es.exists(index="restrictions", id=uid):
        es.index(index="restrictions", id=uid, body=json_object)

# https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def findElements(URL,target,value):
    from selenium import webdriver

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'lxml')

    element = ""

    if target == 'Text':
        texts  = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts )
        element = element.join(t.strip() for t in visible_texts).strip()
        print(element)

    elif target == 'CSSselector':
        element = soup.select(value)

    else:
        kwargs = ""
        if "[" in value: # a list
            kwargs = ""
        else:
            kwargs = {
                target: value
            }
        element = soup.find_all(**kwargs)

    if not element:
        # use selenium
        driver = webdriver.Chrome()
        driver.get(URL)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        element = soup.select(value)

    return element

if __name__ == '__main__':

    sources = pd.read_csv("urls.csv", sep=";")
    es = Elasticsearch()
    es.indices.create(index="restrictions", ignore=400)

    for index, row in sources.iterrows():

        logging.info("Starting scraping for %s with URL %s",row.State, row.URL)

        element = findElements(row.URL, row.Target, row.Value)

        if element:
            restrictionData = dict.fromkeys(attributes)
            restrictionData['federateState'] = str(row.State)
            restrictionData['creationDate'] = datetime.now().strftime("%d-%m-%Y")
            restrictionData['incidenceBased'] = False

            directory = "measures/" + restrictionData["federateState"] + "/" + datetime.now().strftime("%d-%m-%Y_%H-%M/")

            if element[0].name == "img": #-> multiple images
                imgURLs = [getImgURLfromElem(elem) for elem in element]
                imgURLs = [elem for elem in imgURLs if elem is not None] # Filters empty urls - guess not necessary anymore
                if imgURLs:
                    txtData = saveImagesFromPage(imgURLs, directory)
                    getInformationFromData(txtData, restrictionData)
                else:
                    logging.error("Couldn't find any images for URL %s", row.URL)

            elif element[0].name == "a": #-> PDF
                pdfURLs = [getPDFURLfromElem(elem) for elem in element]
                if pdfURLs:
                    txtData = savePDFfromPage(pdfURLs, directory)
                    getInformationFromData(txtData, restrictionData)
                else:
                    logging.error("Couldn't find any PDFs for URL %s", row.URL)

            elif element[0].name == 'div': #-> Text
                txtData = "".join(div.text.strip() for div in element)
                savePage(row.URL, directory)
                getInformationFromData(txtData, restrictionData)

            saveMetadata(es, restrictionData)
            logging.info("Scraping for Federate State %s done", restrictionData["federateState"])
        else:
            logging.error("nothing found for URL %s", row.URL)

    logging.info("Scraper finished")
import requests
import re
import urllib
import ssl
import datefinder
import locale
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
# https://regex101.com/r/2BXdcV/1
DATE_REGEX = r"([1-3]?[0-9][.]([ ](Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)([ ]202[0-9])?|[0-1]?[0-9][.]?(202[0-9])?))"
# https://regex101.com/r/4J8BJ9/1
INCIDENCE_REGEX = r"(?<=Inzidenzstufe \d \n[(]).*(?=\))"

attributes = ["validFrom", "incidenceBased", "federateState", "creationDate", "incidenceSteps", "tags"]
tags = ["Maskenpflicht", "Kontaktbeschrankung", "Veranstaltungen", "Kultur", "Gastronomie", "Schule", "Sport"]

def getImgURLfromElem(elem):
    #if "Regeln" in elem['alt'] or "Regelung" in elem['alt']:
    srcSet = elem.attrs['srcset']
    srcSet = srcSet.split(',')

    srcSet = ['http' + re.search('http(.*).png', str).group(1) + '.png' for str in srcSet]
    srcSet.sort()
    # brauchen wir alle Links zu den Bildern?
    # hol mir jetzt mal nur das größte Bild weil geile Auflösung
    size = len(srcSet)
    imgURL = srcSet[size - 1]
    logging.info("Filtering found Img-Element %s", imgURL)
    return imgURL

def getPDFURLfromElem(elem):


    pdfURL = row.URL[:row.URL.index(".de")+4] + elem["href"]
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

def saveImagesFromPage(imgURLs, directory):

    fileNames = [""] * len(imgURLs)
    incidenceRanges = [""] * len(imgURLs)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for index, imgURL in enumerate(imgURLs, start=0):
        incidenceRanges[index] = re.search('ueberblick_(.*).png', imgURL).group(1)
        #fileNames[index] = datetime.now().strftime("%d-%m-%Y_%H-%M-%S/")+ restrictionData["federateState"] + "_" + incidenceType + ".png"
        fileNames[index] = directory+incidenceRanges[index] + ".png"
        #TODO: save raw data to hadoop
        logging.info("downloading File %s", fileNames[index])
        urllib.request.urlretrieve(imgURL, fileNames[index])

    return fileNames, incidenceRanges

def savePDFfromPage(pdfURLs, directory):

    fileNames = [""] * len(pdfURLs)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for index, pdfURL in enumerate(pdfURLs, start=0):

        fileNames[index] = directory + pdfURL[pdfURL.rindex("/")+1:pdfURL.rindex(".")] + ".pdf"
        logging.info("downloading File %s", fileNames[index])
        urllib.request.urlretrieve(pdfURL, fileNames[index])

    return fileNames

def extractDate(data):
    beginDateStr = re.search(DATE_REGEX, data, re.IGNORECASE).group()
    if any(c.isalpha() for c in beginDateStr) and not beginDateStr[-1].isnumeric():
        now = datetime.now()
        beginDateStr += " " + str(now.year)
    locale.setlocale(locale.LC_ALL, "german")
    return datetime.strptime(beginDateStr, '%d. %B %Y')

def checkForTags(restrictionData, data, tags):
    for tag in tags:
        if tag in data:
            if restrictionData['tags'] is None:
                restrictionData['tags'] = [tag]
            else:
                if tag not in restrictionData['tags']:
                    restrictionData['tags'].append(tag)
        else:
            continue

def getInformationFromPDF(pdfFiles):
    if pdfFiles:
        for index, pdfFile in enumerate(pdfFiles, start=0):
            logging.info("analyzing Metadata for file %s", pdfFile)

            with open(pdfFile, 'rb') as fin:
                data = pdfminer.high_level.extract_text(fin,codec='utf-8')
            with open(pdfFile + ".txt", "w") as text_file:
                text_file.write(data)

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


def getInformationFromImages(imgFiles, incidenceRanges):

    if imgFiles:
        for index, imgFile in enumerate(imgFiles, start=0):

            logging.info("analyzing Metadata for file %s", imgFile)

            data = pytesseract.image_to_string(Image.open(imgFile))

            with open(imgFile + ".txt", "w") as text_file:
                text_file.write(data)

            if index==0:
                restrictionData['validFrom'] = extractDate(data).strftime("%d-%m-%Y")

            if incidenceRanges[index].startswith("u"):
                incidenceStep = "<"+incidenceRanges[index][1:]
            else:
                incidenceStep = ">"+incidenceRanges[index][0:2]

            if restrictionData["incidenceSteps"] is None:
                restrictionData["incidenceSteps"] = [incidenceStep]
            else:
                restrictionData["incidenceSteps"].append(incidenceStep)

            checkForTags(restrictionData, data, tags)

    else:
        logging.error("Couldn't find any images for URL %s", URL)

def saveMetadata():
    # send metadata to elastic search
    fileName = directory+"data.json"
    with open(fileName, 'w') as outfile:
        logging.info("writing Metadata-JSON to File %s", fileName)
        json.dump(restrictionData, outfile)

    logging.info("writing Metadata-JSON to Elasticsearch")
    json_object = json.dumps(restrictionData)

    es = Elasticsearch()
    es.indices.create(index="restrictions", ignore=400)
    es.index(index="restrictions", body=json_object)

if __name__ == '__main__':

    sources = pd.read_csv("urls.csv", sep=";")

    for index, row in sources.iterrows():

        logging.info("Starting scraping for %s with URL %s",row.State, row.URL)

        restrictionData = dict.fromkeys(attributes)
        restrictionData['incidenceBased'] = True
        restrictionData['federateState'] = str(row.State)
        restrictionData['creationDate'] = datetime.now().strftime("%d-%m-%Y")

        directory = "measures/" + restrictionData["federateState"] + "/" + datetime.now().strftime("%d-%m-%Y_%H-%M/")

        page = requests.get(row.URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        if row.Target != 'CSSselector':
            kwargs = {
                row.Target : row.Value
            }
            element = soup.find_all(**kwargs)
        else:
            element = soup.select(row.Value)

        if element[0].name == "img": #-> multiple images
            imgURLs = [getImgURLfromElem(elem) for elem in element]
            #imgURLs = [elem for elem in imgURLs if elem is not None] # Filters empty urls - guess not necessary anymore
            imgFiles, incidenceRanges = saveImagesFromPage(imgURLs, directory)
            getInformationFromImages(imgFiles, incidenceRanges)
        elif element[0].name == "a": #-> PDF
            pdfURLs = [getPDFURLfromElem(elem) for elem in element]
            pdfFiles = savePDFfromPage(pdfURLs, directory)
            getInformationFromPDF(pdfFiles)

        saveMetadata()
        logging.info("Scraping for Federate State %s done", restrictionData["federateState"])

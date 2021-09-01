from bs4 import BeautifulSoup
from bs4.element import Comment
from Config import *
from Util import *
import requests
import pdfminer.high_level
import os
import urllib
import pytesseract

try:
    from PIL import Image
except ImportError:
    import Image

import logging
logger = logging.getLogger(loggerName)

class Parser:

    def __init__(self, hdfs_client, directory, url, target, value):
        self.hdfs_client = hdfs_client
        self.directory = directory
        self.baseUrl = url
        self.target = target
        self.val = value
        pytesseract.pytesseract.tesseract_cmd = 'E:/Programme/Tesseract/tesseract'

    def findElements(self):
        page = requests.get(self.baseUrl)
        soup = BeautifulSoup(page.content, 'lxml')

        elements = ""

        if self.target == 'Text':
            #deprecated?
            texts = soup.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            elements = elements.join(t.strip() for t in visible_texts).strip()

        elif self.target == 'CSSselector':
            elements = soup.select(self.val)

        else:
            kwargs = {
                    self.target: self.val
                }
            elements = soup.find_all(**kwargs)

        return self.filterElements(elements)

    # https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def filterElements(self, elements):

        resultSet = []
        for (index, element) in enumerate(elements, 0):
            if element.name == "img":
                val = "src"

            elif element.name == "a":
                val = "href"

            elif element.name == 'div':
                resultSet.extend([("Text",element)])
                continue
            else:
                logger.error("Unknown element found: %s", element)
                continue

            url = element[val]
            url = fixURL(self.baseUrl, url)
            if url:
                logging.info("Filtering found Element %s", url)
                resultSet.extend([("File", url)])

        return resultSet


    def parse(self):

        elements = self.findElements()
        if elements:
            dataStr = ""

            for type, element in elements:
                  dataStr += self.downloadAndConvertFiles(type, element)

            return dataStr


    def downloadAndConvertFiles(self, type, elem):

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        data = ""
        if type == "Text":
            data = '\n' + elem.text.strip()

            logging.info("downloading File %s", self.baseUrl)
            response = urllib.request.urlopen(self.baseUrl)
            webContent = response.read()

            open(self.directory+DEFAULT_HTML_FILENAME, 'wb').write(webContent)

#            self.hdfs_client.save_as_file(self.directory+DEFAULT_HTML_FILENAME, webContent)
        else:
            url = elem

            # clean url
            if not url.find('?') < 1:
                cleanedUrl = url[:url.find('?')]
            else:
                cleanedUrl = url

            path, dataType = os.path.splitext(cleanedUrl)
            if not dataType:
                dataType = dataType[:-1] + ".pdf"
                url = url + dataType

            fileName = self.directory + url[url.rindex("/") + 1:url.rindex(".")] + dataType

            if dataType == ".pdf":
                logging.info("downloading File %s", url)
                urllib.request.urlretrieve(url, fileName)

                with open(fileName, 'rb') as pdfFile:
                    #bytes = pdfFile.read()
                    #self.hdfs_client.save_as_file(fileName, bytes.decode("utf-8"))
                    logging.info("extracting text from pdf..")
                    data = '\n' + pdfminer.high_level.extract_text(pdfFile, codec="utf-8")

                #os.remove(fileName)

            else:


                #fileNameBG = fileName[:fileName.rindex(".")] + "BG" + dataType
                fileNameBW = fileName[:fileName.rindex(".")] + "BW" + dataType

                logging.info("downloading File %s", cleanedUrl)
                urllib.request.urlretrieve(cleanedUrl, fileName)

                logging.info("converting %s into B&G", fileName)
                #imgBG = Image.open(fileName).convert("L")
                imgBW = Image.open(fileName).convert("1", dither=Image.NONE)

                #imgBG.save(fileNameBG)
                imgBW.save(fileNameBW)

                logging.info("extracting text from image..")
                data = '\n' + pytesseract.image_to_string(imgBW, lang='deu')

        return data
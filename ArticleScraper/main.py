import ArgumentParserWrapper
import ArticleScraper
import logging
from Config import STANDARD_FORMAT 


if __name__ == '__main__':

    logging.basicConfig(format='[%(levelname)s][%(asctime)s]: %(message)s', datefmt = STANDARD_FORMAT, level=logging.DEBUG)
    logging.info("Start Scraper")
    
    scraper = ArticleScraper()
    parser = ArgumentParserWrapper()

    for source in parser.parse_data_from_arguments():
            scraper.scrape(source)

    logging.info("Close Scraper")





    
    

    
    

from argument_parser_wrapper import ArgumentParserWrapper
from article_scraper import ArticleScraper
import logging
from config import STANDARD_LOG_DATE_FORMAT, STANDARD_LOG_FORMAT


if __name__ == '__main__':

    logging.basicConfig(format=STANDARD_LOG_FORMAT, datefmt = STANDARD_LOG_DATE_FORMAT, level=logging.DEBUG)
    logging.info("Start Scraper")
    
    scraper = ArticleScraper()
    parser = ArgumentParserWrapper()

    for source in parser.parse_data_from_arguments():
            scraper.scrape(source)

    logging.info("Close Scraper")





    
    

    
    

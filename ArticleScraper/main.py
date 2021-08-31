from argument_parser_wrapper import ArgumentParserWrapper
from article_scraper import ArticleScraper
import logging
import utils


if __name__ == '__main__':

    utils.init_global_config("..\config\config.json")

    logging.basicConfig( format = utils.config["STANDARD_LOG_FORMAT"], datefmt = utils.config["STANDARD_LOG_DATE_FORMAT"], level=logging.INFO)
    logging.info("Start Scraper")
    
    scraper = ArticleScraper()
    parser = ArgumentParserWrapper()

    for source in parser.parse_data_from_arguments():
            scraper.scrape(source)

    logging.info("Close Scraper")





    
    

    
    

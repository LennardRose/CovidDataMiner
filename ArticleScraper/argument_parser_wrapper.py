from repository import Repository
import argparse
import sys


class ArgumentParserWrapper: # clap the sillables like a 3 year old

    def __init__(self):
        self.repository = Repository()
        self.parser = argparse.ArgumentParser(description='scrapes sources by the configs given')

    def parse_arguments(self):
        """
        parses the arguments
        """


        self.parser.add_argument("-e", "--elasticsearch", action="append", dest="elastic_ids", default=[],
                            help="config stored in elasticsearch, add id of the config")

        self.parser.add_argument("-f", "--file", action="append", dest="filenames", default=[],
                            help="config stored in file, add filename")

        return self.parser.parse_args()

        

    def parse_data_from_arguments(self):
        """
        retrieves the source configurations mentioned in the arguments
        :return: all found data
        """

        args = self.parse_arguments()
        data = []

        if len(sys.argv) < 2: #programmname ist auch ein argument, deshalb 2 ---> scrape alle in elasticsearch wenn nichts weiter angegeben
            data = self.repository.get_all_article_configs()

        for filename in args.filenames:
            data.append(self.repository.open_file(filename))
                
        for id in args.elastic_ids:
            data.append(self.repository.get_article_config(id))

        data = list(filter(None, data)) # filter the none values for missing values

        return data
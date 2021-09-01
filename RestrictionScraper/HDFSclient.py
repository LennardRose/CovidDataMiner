from Config import *
import logging
logger = logging.getLogger(loggerName)


class HDFSClient:

    def save_as_file(self, filename, content):
        """
        saves the content with a given filename as a file
        """
        with open("hdfs/"+filename, "w") as file:
                file.writelines(content)


    def open_file(self, filename):
        """
        opens the file by filename
        """
        try:
            with open("hdfs/"+filename, "r") as file:
                return json.load(file)
        except:
            logger.error("hdfs/"+filename + " not found.")

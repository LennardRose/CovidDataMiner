import json
import utils
import logging

class meta_parser:
    """
    parses meta data from given soup based on the specifications in the meta_config

    """

    def __init__(self, URL, soup, meta_config):

        self.meta_config = meta_config
        self.soup = soup
        self.meta_data = { "title" : None, 
            "description" : None, 
            "url": URL,  #wird direkt übergeben um sie nicht nochmal auslesen zu müssen
            "source_url" : meta_config["base_url"] + meta_config["path_url"],  #wird gebraucht um später doppelte ergebnisse zu vermeiden und um bei mehreren scrapern pro website verwechslungen zu vermeiden
            "type" : None, 
            "date" : None, 
            "index_time" : utils.date_now(),  #wichtig mit millisekunden
            "region" : meta_config["region"], 
            "site_name" : meta_config["site_name"], 
            "author" : None, 
            "keywords" : None,
            "filename" : "placeholder_to_prevent_iteration"}



    def get_meta_data(self):
        """
        returns the meta_data
        """
        return self.meta_data



    def parse_metadata(self):
        """
        chooses a parsing strategy for every meta attribute based on the given source set in the meta_config to set the value
        sets the filename
        """
        for key in self.meta_data.keys():

            if self.meta_data[key] == None:

                if self.meta_config[key]["source"] == "NOEXIST":
                    self.set_noexist(key)

                elif self.meta_config[key]["source"] == "DEFAULT":
                    self.set_default(key)

                elif self.meta_config[key]["source"] == "TAG":
                    self.parse_from_tag(key)

                elif self.meta_config[key]["source"] == "JSON_LD":
                    self.parse_from_json(key)

                else:
                    logging.error("No meta-config found for: " + (str(self.meta_data[key]) if self.meta_data[key] else " <not found>") + 
                    ", config was: " + (str(self.meta_config[key]) if self.meta_config[key] else " <not found>"))

        self.set_filename()


    def set_filename(self):
        self.meta_data["filename"] = self.meta_config["region"] + "_" + self.meta_config["site_name"] + "_" + utils.slugify(self.meta_data["title"]) + ".txt"


    def set_noexist(self, key):
        if  key == "title" or key == "date":
            logging.error("Forbidden attribute value NOEXIST for "+ key +" meta data.")
        
        self.meta_data[key] = "-" #überlegen welches freizeichen 



    def set_default(self, key):
        """
        set the keys default value
        error if the key is title, title must be unique for filename
        default date is the current date
        every other key is set from meta_configs default value
        """

        if key == "title":
            logging.error("Forbidden attribute value DEFAULT for title meta data.")

        elif key == "date":
            self.meta_data[key] = utils.date_now()

        else:
            self.meta_data[key] = self.meta_config[key]["default"]

        if self.meta_data[key] == None or self.meta_data[key] == "":
            logging.warning("No default-value set for " + key)



    def parse_from_tag(self, key):
        """
        parses meta value from any given tag/attribute/attribute_value combination
        takes care of right format
        """
        
        tag = self.soup.find(self.meta_config[key]["tag"], { self.meta_config[key]["attribute"] : self.meta_config[key]["attribute_value"]})

        if tag:

            if key == "date":
                self.meta_data[key] = utils.parse_date(self.get_content(tag))

            else:
                self.meta_data[key] = self.get_content(tag)



    def get_content(self, tag):
        """
        get content of given tag, if tag has some nested tags inside of which one is holding the content, it returns the first content
        example:
        right result will be returned: <div><span><a>right</a></span></div> 
        wrong result will be returned: <div><span>wrong<a>right</a></span></div>
        """
        if tag.is_empty_element and tag.get("content", None) != None and tag.get("content", None) != "":
            return tag.get("content", None)
        elif not tag.is_empty_element:
            return tag.text
        else:
            for child in tag.descendants:
                return self.get_content(child) # rekursiv vielleicht bisschen zu unperformant

        logging.error("No content in tag: " + tag.get("name", None) if tag else "<tag not found>" + " found.")

        

    def parse_from_json(self, key):
        """
        uses the <script type=application/ld+json> to retrieve meta information
        even thoug script is the tag, type the attribute and application/... the attribute value, 
        we will use the tag property of the meta_config as the json-key, the attribute and attribute_value
        porperty to choose wich application/ld+json tag to use if there are multiple
        retrieves all ld+json scripts on the page and iterates through all for the needed value
        """
        if self.meta_config[key]["attribute"] == None and self.meta_config[key]["attribute_value"] == None:
            result_set = self.soup.find_all('script', {'type':'application/ld+json'}) 
        else:
            result_set = self.soup.find_all('script', {'type':'application/ld+json', self.meta_config[key]["attribute"] : self.meta_config[key]["attribute_value"]}) 

        if result_set:
            result = []

            for element in result_set:

                element = element.text.strip()
                result.append(json.loads( element ))



            if result: # find_all returns a list

                for scripts in result: #json+ld script may consist of other scripts

                    if type(scripts) is list: #check ob json liste

                        for script in scripts:
                            self.get_json_value(script, key)

                    else: 
                        self.get_json_value(scripts, key)
        


    def get_json_value(self, script, key):
        """
        set the meta_data of the given key if the json-key is in the given script
        """

        if self.meta_config[key]["tag"] in script:

            content = script[self.meta_config[key]["tag"]]
            result = ""

            if type(content) is list:
                for element in content:
                    if "name" in element:
                        result += str(element["name"])

            elif type(content) is dict:
                result = content["name"]

            else: 
                result = content

            if key == "date":
                self.meta_data[key] = utils.parse_date(result)

            else:
                self.meta_data[key] = result 






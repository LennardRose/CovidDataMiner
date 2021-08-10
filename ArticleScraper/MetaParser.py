import json
import utils
import logging

class meta_parser:

    def __init__(self, URL, soup, meta_config):

        self.meta_config = meta_config
        self.soup = soup
        self.meta_data = { "title" : None, 
            "description" : None, 
            "url": URL, 
            "type" : None, 
            "date" : None, 
            "index_time" : utils.date_now(),
            "city" : meta_config["city"], 
            "site_name" : meta_config["site_name"], 
            "author" : None, 
            "keywords" : None,
            "filename" : "placeholder_to_prevent_iteration"}

    def parse_metadata(self):
        """
        parses meta data from given soup based on the specifications in source
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

        return self.meta_data

    def set_filename(self):
        self.meta_data["filename"] = self.meta_config["city"] + "_" + self.meta_config["site_name"] + "_" + self.meta_data["title"] + ".txt"


    def set_noexist(self, key):
        if  key == "title" or key == "date":
            logging.error("Forbidden attribute value NOEXIST for "+ key +" meta data.")
        
        self.meta_data[key] = "-" #überlegen welches freizeichen 

    def set_default(self, key):

        if key == "title":
            logging.error("Forbidden attribute value DEFAULT for title meta data.")

        elif key == "date":
            self.meta_data[key] = utils.date_now()

        else:
            self.meta_data[key] = self.meta_config[key]["default"]

    def parse_from_tag(self, key):
        """
        parses meta value from any given tag/attribute/attribute_value combination
        takes care of right format
        """
        
        tag = self.soup.find(self.meta_config[key]["tag"], { self.meta_config[key]["attribute"] : self.meta_config[key]["attribute_value"]})

        if tag:

            if key == "title":

                self.meta_data[key] = utils.slugify(self.get_content(tag))

            elif key == "date":
                self.meta_data[key] = utils.parse_date(self.get_content(tag))

            else:
                self.meta_data[key] = self.get_content(tag)
        

    def parse_from_json(self, key):
        """
        uses the <script type=application/ld+json> to retrieve meta information
        even thoug script is the tag, type the attribute and application/... the attribute value, 
        we will use the tag property of the meta_config as the json-key, the attribute and attribute_value
        porperty to choose wich application/ld+json tag to use if there are multiple
        takes care of right format
        """
        if self.meta_config[key]["attribute"] == None and self.meta_config[key]["attribute_value"] == None:
            scripts = json.loads( self.soup.find('script', {'type':'application/ld+json'}).text.strip() )
        else:
            scripts = json.loads( self.soup.find('script', {'type':'application/ld+json', self.meta_config[key]["attribute"] : self.meta_config[key]["attribute_value"]}).text.strip() )

        if scripts:

            if type(scripts) == list: #check ob json liste

                for script in scripts:
                    self.get_json_value(script, key) #rekursiv whoopsie

            else: 
                self.get_json_value(scripts, key)
        


    def get_json_value(self, scripts, key):
        try:
            if scripts[self.meta_config[key]["tag"]]:
        
                if key == "title":
                    self.meta_data[key] = utils.slugify(scripts[self.meta_config[key]["tag"]])

                elif key == "date":
                    self.meta_data[key] = utils.parse_date(scripts[self.meta_config[key]["tag"]])

                else:
                    self.meta_data[key] = scripts[self.meta_config[key]["tag"]] 
        except: #keyerror abfangen bis ich weiß wie man in nem json check ob key vorhanden ist
            pass


    def get_content(self, tag):
        """
        get content of given tag, if tag has some nested tags inside of which one is holding the content, it returns the first content
        example:
        right result will be returned: <div><span><a>right</a></span></div> 
        wrong result will be returned: <div><span>wrong<a>right</a></span></div>
        """
        if not tag.is_empty_element:
            return tag.text
        if tag.get("content", None) != None and tag.get("content", None) != "":
            return tag.get("content", None)
        else:
            for child in tag.descendants:
                return self.get_content(child) # rekursiv vielleicht bisschen zu unperformant

        logging.error("No content in tag: " + tag if tag else "<not found>" + " found.")



class source_object:

    def __init__(self, city, site_name, base_url, path_url, html_tag = None, html_class = None, condition = None, include_condition = None,
                 title_source = "STANDARD", title_tag = None, title_attribute = None, title_attribute_value = None,
                 date_source = None, date_tag = None, date_attribute = None, date_attribute_value = None,
                 author_source = None, author_tag = None, author_attribute = None, author_attribute_value = None, author_default = None,
                 description_source = "NOEXIST", description_tag = None, description_attribute = None, description_attribute_value = None, description_default = None,
                 type_source = "NOEXIST", type_tag = None, type_attribute = None, type_attribute_value = None, type_default = None,
                 keywords_source = "NOEXIST", keywords_tag = None, keywords_attribute = None, keywords_attribute_value = None, keywords_default = None
                 ):
        self.city = city
        self.site_name = site_name
        self.base_url = base_url
        self.path_url = path_url
        self.html_tag = html_tag
        self.html_class = html_class
        self.condition = condition
        self.condition_boolean = include_condition
        self.title = { "source" : title_source,
                        "tag" : title_tag,
                        "attribute" : title_attribute,
                        "attribute_value" : title_attribute_value
                        }
        self.date = { "source" : date_source,
                        "tag" : date_tag,
                        "attribute" : date_attribute,
                        "attribute_value" : date_attribute_value
                        }
        self.author = { "source" : author_source,
                        "tag" : author_tag,
                        "attribute" : author_attribute,
                        "attribute_value" : author_attribute_value,
                        "default" : author_default
                        }
        self.description = { "source" : description_source,
                        "tag" : description_tag,
                        "attribute" : description_attribute,
                        "attribute_value" : description_attribute_value,
                        "default" : description_default
                        }
        self.type = { "source" : type_source,
                        "tag" : type_tag,
                        "attribute" : type_attribute,
                        "attribute_value" : type_attribute_value,
                        "default" : type_default
                        }
        self.keywords = { "source" : keywords_source,
                        "tag" : keywords_tag,
                        "attribute" : keywords_attribute,
                        "attribute_value" : keywords_attribute_value,
                        "default" : keywords_default
                        }



    
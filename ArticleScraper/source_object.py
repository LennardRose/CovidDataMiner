class source_object:

    def __init__(self, city, site_name, base_url, path_url, html_tag = None, html_class = None, condition = None, condition_boolean = None,
    title_source = "STANDARD", title_tag = None, title_class = None, 
    date_source = None, date_tag = None, date_class = None, 
    author_source = None, author_tag = None, author_class = None, author_default = None, 
    description_source = "NOEXIST", description_tag = None, description_class = None, description_default = None, 
    type_source = "NOEXIST", type_tag = None, type_class = None, type_default = None, 
    keywords_source = "NOEXIST", keywords_tag = None, keywords_class = None, keywords_default = None
    ):
        self.city = city
        self.site_name = site_name
        self.base_url = base_url
        self.path_url = path_url
        self.html_tag = html_tag
        self.html_class = html_class
        self.condition = condition
        self.condition_boolean = condition_boolean
        self.title = { "source" : title_source,
                        "tag" : title_tag,
                        "class" : title_class
                        }
        self.date = { "source" : date_source,
                        "tag" : date_tag,
                        "class" : date_class
                        }
        self.author = { "source" : author_source,
                        "tag" : author_tag,
                        "class" : author_class,
                        "default" : author_default
                        }
        self.description = { "source" : description_source,
                        "tag" : description_tag,
                        "class" : description_class,
                        "default" : description_default
                        }
        self.type = { "source" : type_source,
                        "tag" : type_tag,
                        "class" : type_class,
                        "default" : type_default
                        }
        self.keywords = { "source" : keywords_source,
                        "tag" : keywords_tag,
                        "class" : keywords_class,
                        "default" : keywords_default
                        }



    
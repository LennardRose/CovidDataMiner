class source_object:

    def __init__(self, filename, base_url, path_url, html_tag = None, html_class = None, condition = None, condition_boolean = None):
        self.filename = filename
        self.base_url = base_url
        self.path_url = path_url
        self.html_tag = html_tag
        self.html_class = html_class
        self.condition = condition
        self.condition_boolean = condition_boolean
    
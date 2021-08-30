import json
import time

def replace_all_mutated_vowels(json_object):
    """Replaces all 'Umlaute' or mutated vowels in a json object
        does this by converting to string and then replacing and then back to json object


        Args:
            json_object (dict): json object you want to filter

        Returns:
            dict: filtered json object
        """
    string = repr(json_object)
    string = string.replace(chr(252), 'ue')
    string = string.replace(chr(246), 'oe')
    string = string.replace(chr(228), 'ae')
    string = string.replace(chr(214), 'Oe')
    string = string.replace(chr(220), 'Ue')
    string = string.replace(chr(196), 'Ae')
    string = string.replace('\'', '"')
    return json.loads(string)


def current_milli_time():
    """get current time in milliseconds
    Returns:
        int: current time milliseconds
    """
    return round(time.time() * 1000)
import re

import requests
from requests.exceptions import ConnectionError


def only_keep_UTF_8_chars(text):
    output = ''.join([char for char in text if char.encode('utf-8', 'ignore')])
    output = re.sub(r'[^\x00-\x7F]+', '', output)
    return output


def safe_get(link: str):
    try:
        return requests.get(link)
    except ConnectionError as e:
        print("error happend: " + str(e))
        # exit(1)
        return ""

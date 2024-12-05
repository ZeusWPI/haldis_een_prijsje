import re

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError


def fetch_and_parse_html(url: str) -> BeautifulSoup:
    response = safe_get(url)
    if response == "":
        return None
    return BeautifulSoup(response.text, 'html.parser')

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


def extract_spans(div):
    """Extract all non-empty text content from a div, preserving structure with inline elements like <br>."""
    results = []
    for span in div.find_all('span', recursive=True):
        if span.text.strip():  # Check for non-empty text
            results.append(''.join(span.stripped_strings))
    return results


def filter_divs(soup, class_name, condition):
    """
    Filter divs based on a user-defined condition.

    :param soup: BeautifulSoup object containing the HTML content.
    :param condition: A callable that takes a div and returns True if the div should be included.
    :return: A list of divs that match the condition.
    """
    candidate_divs = soup.find_all('div', class_=class_name)
    return [div for div in candidate_divs if condition(div)]


def create_heading_contains_h2_with(text_to_search):
    """
    Create a function that checks if a div contains an h2 with the given text.

    :param text_to_search: The text to search for in the h2 tag.
    :return: A function that takes a div and returns True if the div contains an h2 with the given text.
    """

    def heading_contains_h2_with(div):
        h2_tag = div.find('div', class_='elementor-widget-container').find('h2', string=lambda
            text: text_to_search in text if text else False)
        return h2_tag is not None

    return heading_contains_h2_with

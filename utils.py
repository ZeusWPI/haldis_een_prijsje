import re

import PyPDF2
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
import pdfplumber


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


def download_pdf(url, save_path):
    """Download a PDF from a URL and save it locally."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"PDF downloaded and saved to {save_path}")
    except requests.RequestException as e:
        print(f"Failed to download PDF: {e}")


def parse_pdf(file_path, coords=None):
    """
    Extract and print text from a PDF file.
    If coords is provided, it will extract text from the rectangle defined by these coordinates.
    Coordinates are provided as a tuple: (x0, top, x1, bottom).
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # print(f"\n--- Page {page_number} ---")

                if coords:
                    # Crop the page using the specified rectangle (coords)
                    cropped_page = page.within_bbox(coords)
                    return cropped_page.extract_text()
                else:
                    # Extract text from the entire page
                    return page.extract_text()
    except Exception as e:
        print(f"Failed to parse PDF: {e}")


def get_page_dimensions(file_path, page_number=1):
    """
    Get the dimensions of a specific page in a PDF.

    Args:
    file_path (str): Path to the PDF file.
    page_number (int): The page number (1-based index).

    Prints the width and height of the page in points.
    """
    try:
        # Open the PDF file
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Load the specified page (page_number is 1-based, so subtract 1 for 0-based index)
            page = reader.pages[page_number - 1]

            # Extract the dimensions (in points)
            width = float(page.mediabox[2] - page.mediabox[0])
            height = float(page.mediabox[3] - page.mediabox[1])

            # Print the dimensions
            # print(f"Page {page_number} dimensions: Width = {width} points, Height = {height} points")
            return width, height

    except Exception as e:
        print(f"Failed to retrieve page dimensions: {e}")

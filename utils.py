import functools
import re
import time
from typing import Callable, Optional, List, Tuple

import PyPDF2
import pdfplumber
import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import ConnectionError
from selenium.common.exceptions import StaleElementReferenceException


def sanitize_id(input_str):
    # Keep only characters matching the pattern [a-z0-9_-]
    sanitized = re.sub(r'[^a-z0-9_-]', '', input_str.lower().replace(" ", "_"))
    return sanitized


def timer(func: Callable) -> Callable:
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def comma_float(inp: str) -> float:
    return float(inp.replace(',', '.'))


def fetch_and_parse_html(url: str) -> Optional[BeautifulSoup]:
    response = safe_get(url)
    if response == "":
        return None
    return BeautifulSoup(response.text, 'html.parser')


def only_keep_UTF_8_chars(text: str) -> str:
    output = ''.join([char for char in text if char.encode('utf-8', 'ignore')])
    output = re.sub(r'[^\x00-\x7F]+', '', output)
    return output


def safe_get(link: str) -> Response | str:
    try:
        return requests.get(link)
    except ConnectionError as e:
        print("error happend: " + str(e))
        # exit(1)
        return ""


def extract_spans(div) -> List[str]:
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
    :param class_name: name of the class to filter by.
    :param condition: A callable that takes a div and returns True if the div should be included.
    :return: A list of divs that match the condition.
    """
    candidate_divs = soup.find_all('div', class_=class_name)
    return [div for div in candidate_divs if condition(div)]


def condition_has_text(div) -> bool:  # README
    """
    A condition function to check if a div contains text.

    :param div: A BeautifulSoup tag object representing a div.
    :return: True if the div contains non-empty text; False otherwise.
    """
    return bool(div.get_text(strip=True))


def list_p_tags_in_div(div):  # README
    """
    List all <p> tags within a given <div>.

    :param div: A BeautifulSoup tag object representing a <div>.
    :return: A list of <p> tag elements within the <div>.
    """
    return div.find_all('p')


def get_non_empty_p_texts(div):  # README
    """
    Extract text from all <p> tags within a <div>, keeping only non-empty texts.
    only_keep_UTF_8_chars

    :param div: A BeautifulSoup tag object representing a <div>.
    :return: A list of non-empty text content from <p> tags within the <div>.
    """
    return [
        only_keep_UTF_8_chars(p.get_text(separator=' ', strip=True))
        for p in div.find_all('p')
        if only_keep_UTF_8_chars(p.get_text(separator=' ', strip=True))
    ]


def create_heading_contains_h2_with(text_to_search):
    """
    Create a function that checks if a div contains an h2 with the given text.

    :param text_to_search: The text to search for in the h2 tag.
    :return: A function that takes a div and returns True if the div contains an h2 with the given text.
    """

    def heading_contains_h2_with(div):
        h2_tag = div.find('div', class_='elementor-widget-container').find(
            'h2', string=lambda text: text_to_search in text if text else False)
        return h2_tag is not None

    return heading_contains_h2_with


def download_pdf(url: str, save_path: str) -> None:
    """Download a PDF from a URL and save it locally."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"PDF downloaded and saved to {save_path}")
    except requests.RequestException as e:
        print(f"Failed to download PDF: {e}")


def parse_pdf(file_path: str, coords: Tuple[int, int, int, int] = None) -> str:
    """
    Extract and return text from a PDF file.
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
        return ""


def parse_pdf_with_strip_split_enters(file_path: str, coords: Tuple[int, int, int, int] = None) -> List[str]:
    """
    Extract and return text from a PDF file.
    If coords is provided, it will extract text from the rectangle defined by these coordinates.
    Coordinates are provided as a tuple: (x0(left), y0(top), x1(right), y1(bottom)).
    strip the output and split it at each enter
    """
    output = parse_pdf(file_path, coords)
    return output.strip().split("\n")


def parse_pdf_section(pdf_url: str, local_file_path: str, coords: Tuple[int, int, int, int],
                      page_number: int = 1) -> List:
    """
    Downloads a PDF, retrieves its dimensions, and extracts text from a specified section.

    :param pdf_url: URL of the PDF to download.
    :param local_file_path: Local path to save the PDF.
    :param coords: Tuple specifying the coordinates for text extraction (x1, y1, x2, y2).
    :param page_number: Page number to extract dimensions from (default is 1).
    :return: A list of text lines extracted from the specified section.
    """
    download_pdf(pdf_url, local_file_path)
    _, height = get_page_dimensions(local_file_path, page_number=page_number)
    return parse_pdf_with_strip_split_enters(local_file_path, coords=coords)


def get_page_dimensions(file_path: str, page_number: int = 1) -> Tuple[float, float]:
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


def retry_on_stale(max_retries: int = 3, wait_time: int = 1):
    """
    Decorator to retry a function in case of a StaleElementReferenceException.

    :param max_retries: Maximum number of retries before giving up.
    :param wait_time: Time to wait (in seconds) between retries.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except StaleElementReferenceException as e:
                    if attempt < max_retries - 1:
                        print(f"Retrying due to stale element (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)  # Wait before retrying
                    else:
                        raise e  # Reraise the exception if max retries exceeded

        return wrapper

    return decorator


class SeleniumUtils:
    @staticmethod
    @retry_on_stale(max_retries=3, wait_time=1)
    def find_element_with_retry(driver, locator_type, locator):
        """
        Find a single element with retry on stale reference.

        :param driver: Selenium WebDriver instance.
        :param locator_type: Locator type (e.g., By.ID, By.CLASS_NAME).
        :param locator: Locator string.
        :return: The found WebElement.
        """
        return driver.find_element(locator_type, locator)

    @staticmethod
    @retry_on_stale(max_retries=3, wait_time=1)
    def find_elements_with_retry(driver, locator_type, locator):
        """
        Find multiple elements with retry on stale reference.

        :param driver: Selenium WebDriver instance.
        :param locator_type: Locator type (e.g., By.ID, By.CLASS_NAME).
        :param locator: Locator string.
        :return: A list of found WebElements.
        """
        return driver.find_elements(locator_type, locator)

    @staticmethod
    @retry_on_stale(max_retries=3, wait_time=1)
    def click_element_with_retry(element):
        """
        Click on a web element with retry on stale reference.

        :param element: The WebElement to click.
        """
        element.click()

    @staticmethod
    @retry_on_stale(max_retries=3, wait_time=1)
    def get_text_with_retry(element):
        """
        Get text from a web element with retry on stale reference.

        :param element: The WebElement to extract text from.
        :return: The text of the element.
        """
        return element.text

    @staticmethod
    @retry_on_stale(max_retries=3, wait_time=1)
    def send_keys_with_retry(element, keys):
        """
        Send keys to a web element with retry on stale reference.

        :param element: The WebElement to send keys to.
        :param keys: The keys to send.
        """
        element.send_keys(keys)

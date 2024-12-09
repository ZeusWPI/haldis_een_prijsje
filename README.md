# Restaurant Scraper

This project is a Python-based script to scrape product and location data from different restaurant websites. It supports parallel execution for faster processing and makes it easy to add new parsers.

## Features
- Scrapes data from specified restaurants.
- Saves the scraped data to `.hlds` files for further use.
- Supports parallel and sequential execution modes, configurable via a boolean flag.
- Designed to be extendable with new restaurant parsers.

---

## How to Run

### Prerequisites
- Python 3.x installed on your system.
- Install the required dependencies (e.g., `requests`, `BeautifulSoup`, etc.).

### Run the Script
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/ZeusWPI/haldis_een_prijsje.git
    cd haldis_een_prijsje
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Script**:
    To scrape data for a specific restaurant:
    ```bash
    python main.py
    ```
    - Set `restaurant_name` to the desired restaurant (e.g., `"simpizza"`) in the script.
    - Enable or disable parallelism by toggling the `use_parallelism` flag (`True` or `False`).

4. **Run for All Restaurants**:
    Set `run_everything` to `True` in the script to scrape data from all available restaurants.

---

## Configuration
- **restaurant_name**: Set this to the name of the restaurant you want to scrape.
- **use_parallelism**: Set to `True` for parallel execution or `False` for sequential execution.
- **run_everything**: Set to `True` to scrape all restaurants; otherwise, leave it as `False`.

---

## Adding a New Parser
To add support for a new restaurant scraper:

1. **Check for Open Issues**:
   - Navigate to the [Issues](https://github.com/ZeusWPI/haldis_een_prijsje/issues) section of this repository.
   - Look for an unsigned issue related to the new parser.
   - Assign the issue to yourself.

2. **Implement the Parser**:
   - Create a new scraper file under `scrapers/` (e.g., `newrestaurant_scraper.py`).
   - Implement a `get_prices()` method in the new scraper, returning (see interface in `scrapers/scraper.py`):
     - A list of products.
     - Location information.

3. **Add the Parser to the Main Script**:
   - Define a new function in `main.py` (e.g., `run_newrestaurant`):
     ```python
     def run_newrestaurant():
         newrestaurant_products, newrestaurant_location = NewRestaurantScraper.get_prices()
         with open("hlds_files/newrestaurant.hlds", "w", encoding="utf-8") as file:
             file.write(str(newrestaurant_location) + "\n")
             file.write(translate_products_to_text(newrestaurant_products))
         print("newrestaurant done")
     ```
   - Add the function conditionally to the `tasks` list in `main.py`:
     ```python
     if restaurant_name.lower() == "newrestaurant" or run_everything:
         tasks.append(run_newrestaurant)
     ```

4. **Test Your Parser**:
   - Run the script to ensure your parser works as expected.
   - Fix any bugs or errors.

5. **Submit Your Work**:
   - Mark the issue as resolved and create a pull request to merge your changes.

---

## Contribution Guidelines
- Always assign yourself an open issue before starting work.
- Follow the project structure and coding conventions.
- Test your changes thoroughly before submitting a pull request.
- Ensure your code is well-documented.

---

# Utility Functions Documentation

This document provides an overview of all utility functions included in the script.

## `fetch_and_parse_html(url: str) -> BeautifulSoup`
Fetches and parses the HTML content from a given URL.

- **Parameters**: 
  - `url` (str): The URL to fetch.
- **Returns**: A `BeautifulSoup` object containing the parsed HTML, or `None` if fetching fails.

---

## `only_keep_UTF_8_chars(text: str) -> str`
Filters out non-UTF-8 characters from the given text.

- **Parameters**: 
  - `text` (str): The input text to filter.
- **Returns**: A string containing only UTF-8 characters.

---

## `safe_get(link: str)`
Performs a GET request to the given URL and handles `ConnectionError`.

- **Parameters**: 
  - `link` (str): The URL to fetch.
- **Returns**: A `requests.Response` object if successful, or an empty string if a `ConnectionError` occurs.

---

## `extract_spans(div)`
Extracts all non-empty text content from `<span>` elements within a given `<div>`.

- **Parameters**: 
  - `div`: A BeautifulSoup `<div>` element.
- **Returns**: A list of strings containing the extracted text.

---

## `filter_divs(soup, class_name, condition)`
Filters `<div>` elements from a parsed HTML based on a user-defined condition.

- **Parameters**: 
  - `soup`: A `BeautifulSoup` object containing the HTML content.
  - `class_name` (str): The class name of the `<div>` elements to filter.
  - `condition` (callable): A function that takes a `<div>` element and returns `True` if the `<div>` matches the condition.
- **Returns**: A list of `<div>` elements that match the condition.

---

## `create_heading_contains_h2_with(text_to_search)`
Generates a condition function to check if a `<div>` contains an `<h2>` tag with the specified text.

- **Parameters**: 
  - `text_to_search` (str): The text to search for within an `<h2>` tag.
- **Returns**: A function that takes a `<div>` and returns `True` if it contains an `<h2>` tag with the specified text.

---

## `download_pdf(url: str, save_path: str)`
Downloads a PDF from a given URL and saves it locally.

- **Parameters**: 
  - `url` (str): The URL of the PDF to download.
  - `save_path` (str): The local path to save the downloaded PDF.
- **Returns**: None. Prints a success or failure message.

---

## `parse_pdf(file_path: str, coords: tuple = None)`
Extracts text from a PDF file. Optionally extracts text from a specified rectangular region.

- **Parameters**: 
  - `file_path` (str): Path to the PDF file.
  - `coords` (tuple, optional): A tuple defining the rectangle (x0, top, x1, bottom). Defaults to `None` for full-page extraction.
- **Returns**: Extracted text as a string.

---

## `get_page_dimensions(file_path: str, page_number: int = 1)`
Retrieves the dimensions of a specified page in a PDF.

- **Parameters**: 
  - `file_path` (str): Path to the PDF file.
  - `page_number` (int): The 1-based index of the page. Defaults to 1.
- **Returns**: A tuple containing the width and height of the page in points.

## `comma_float(inp: str) -> float`
Converts a string representation of a number with a comma as a decimal separator to a float.

- **Parameters**: 
  - `inp` (str): The input string containing the number (e.g., `"1,23"`).

- **Returns**: 
  - A `float` where commas in the input string are replaced with dots to adhere to standard decimal notation (e.g., `1.23`).

- **Example**:
  ```python
  number = comma_float("1,23")
  print(number)  # Output: 1.23

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

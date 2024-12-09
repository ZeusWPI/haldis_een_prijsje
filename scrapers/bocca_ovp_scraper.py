import time

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By

from data_types.choice import Choice, ChoiceList, ChoiceType
from data_types.location import Location
from data_types.product import Product
from scrapers.scraper import Scraper

from seleniumbase import SB

from utils import download_pdf, parse_pdf, get_page_dimensions, comma_float


# http://www.bocca.be/menus/take-away.html
class BoccaOvpScraper(Scraper):

    @staticmethod
    def get_prices() -> (set[Product], Location):
        start_time = time.time()
        products = set()
        locatie = Location(
            "bocca: Bocca",
            "https://www.openstreetmap.org/node/1462321981#map=19/51.038423/3.726819",
            "Citadellaan 4, 9000 Ghent",
            "+32 (0)9 245 37 99",
            "http://www.bocca.be/"
        )
        # Define the URL and file path
        pdf_url = "http://www.bocca.be/documents/BOCCA_TAKEAWAY.pdf"
        local_file_path = "bocca_takeaway.pdf"

        # Download and parse the PDF
        download_pdf(pdf_url, local_file_path)
        width, height = get_page_dimensions(local_file_path, page_number=1)
        x_lim = 200
        top_y_lim = 200
        bottom_y_lim = 350
        sauce_to_go = parse_pdf(local_file_path, coords=(0, top_y_lim, x_lim, height - bottom_y_lim))

        # Split text by lines, then process each line
        lines = sauce_to_go.strip().split("\n")
        parts = lines[0].split(" ")
        size_small = parts[len(parts) - 2].strip()
        size_large = parts[len(parts) - 1].strip()
        keep_text = ""
        for line in lines[1:]:
            # Split the line by spaces, separating the name and sizes/prices
            parts = line.split(" ")
            name = " ".join(parts[:-2])  # Everything except the last two parts
            if keep_text:
                name = keep_text + " " + name
                keep_text = ""
            name = "SAUCE TO GO " + name

            try:
                keuze_lijst = ChoiceList(name="what size?")
                # Check if the last part is a size/price and collect it
                prize_small = comma_float(parts[len(parts) - 2])
                prize_large = comma_float(parts[len(parts) - 1])
                keuze_lijst.add_choice(Choice(name=size_small, price=0.0))
                keuze_lijst.add_choice(Choice(name=size_large, price=prize_large - prize_small))
            except ValueError:
                keep_text = " ".join(parts)
                continue

            # Create the product object
            product = Product(name=name, price=prize_small)
            product.add_choiceList(keuze_lijst)
            products.add(product)

        left_x_lim = 200
        x_lim = 400
        top_y_lim = 200
        bottom_y_lim = 250
        sizes_section = parse_pdf(local_file_path, coords=(left_x_lim, top_y_lim, x_lim, height - bottom_y_lim))

        groote_keuze = ChoiceList(name="what size?")
        lines = sizes_section.strip().split("\n")
        small_prize = comma_float(lines[0])
        for i in range(0, len(lines) - 1, 2):
            # print(lines[i+1], "costs:", float(lines[i].replace(",", ".")))
            groote_keuze.add_choice(Choice(name=lines[i + 1], price=comma_float(lines[i])-small_prize))


        left_x_lim = 200
        x_lim = 400
        top_y_lim = 670
        bottom_y_lim = 0
        pasta_section = parse_pdf(local_file_path, coords=(left_x_lim, top_y_lim, x_lim, height - bottom_y_lim))

        pasta_keuze = ChoiceList(name="what pasta?")
        lines = pasta_section.strip().split("\n")
        pasta_1 = lines[0].lower()
        pasta_keuze.add_choice(Choice(name=pasta_1, price=0.0))
        pasta_2 = (lines[1] + " " + lines[2]).lower().split("+")
        pasta_keuze.add_choice(Choice(name=pasta_2[0], price=comma_float(pasta_2[1])))
        pasta_3 = (lines[3] + " " + lines[4]).lower().split("+")
        pasta_keuze.add_choice(Choice(name=pasta_3[0], price=comma_float(pasta_3[1])))
        pasta_4 = (lines[5] + " " + lines[6]).lower().split("+")
        pasta_keuze.add_choice(Choice(name=pasta_4[0], price=comma_float(pasta_4[1])))

        left_x_lim = 400
        right_x_lim = 650
        top_y_lim = 125
        bottom_y_lim = 0
        sauce_section = parse_pdf(local_file_path, coords=(left_x_lim, top_y_lim, right_x_lim, height - bottom_y_lim))
        lines = sauce_section.split("\n")

        bocca = Product(name=lines[0].strip(), description=" ".join([lines[1].strip(), lines[2].strip()]), price=small_prize)
        bollo = Product(name=lines[3].strip(), description=lines[4].strip(), price=small_prize)
        cheese_and_ham = Product(name=lines[5].strip(), price=small_prize)
        veggie = Product(name=lines[6].strip(), description=" ".join([lines[7].strip(), lines[8].strip()]), price=small_prize)
        marisol = Product(name=lines[9].strip(), description=" ".join([lines[10].strip(), lines[11].strip()]), price=small_prize)
        four_cheese = Product(name=lines[12].strip(), description=" ".join([lines[13].strip(), lines[14].strip()]), price=small_prize)
        curr_w_wo_smoked_salmon = Product(name=" ".join([lines[15].strip(), lines[16].strip(), lines[17].strip()]),
                                          description=lines[18].strip(), price=small_prize)
        arabiata = Product(name=lines[19].strip(), description=lines[20].strip(), price=small_prize)
        green_pesto = Product(name=lines[21].strip(), description=" ".join([lines[22].strip(), lines[23].strip()]), price=small_prize)
        red_pesto = Product(name=lines[24].strip(), description=" ".join([lines[25].strip(), lines[26].strip()]), price=small_prize)
        potw = Product(name=lines[27].strip(), description=lines[28].strip(), price=small_prize)
        mix_2 = Product(name=lines[29].strip(), price=small_prize)
        mix_3 = Product(name=lines[30].strip().split("+")[0], price=comma_float(lines[30].strip().split("+")[1]) + prize_small)

        left_x_lim = 650
        right_x_lim = width
        top_y_lim = 125
        bottom_y_lim = 250
        toppings_section = parse_pdf(local_file_path, coords=(left_x_lim, top_y_lim, right_x_lim, height - bottom_y_lim))
        lines = toppings_section.split("\n")
        toppings_keuze = ChoiceList(name="what topping?", type=ChoiceType.MULTI)
        toppings_keuze.add_choice(Choice(name=lines[0].strip().split(" ")[0]))
        prev_prod_name = None
        prev_prod_price = None
        for line in lines[1:]:
            try:
                # line.split("+")[1]
                new_prod_name = line.split("+")[0]
                new_prod_price = comma_float(line.split("+")[1])
                if prev_prod_name != None and prev_prod_price != None:
                    toppings_keuze.add_choice(Choice(name=prev_prod_name, price=prev_prod_price))
                prev_prod_name = new_prod_name
                prev_prod_price = new_prod_price
            except IndexError:
                prev_prod_name += line
        toppings_keuze.add_choice(Choice(name=prev_prod_name, price=prev_prod_price))

        mix_keuze = ChoiceList(name="what sauce mix")
        for prod in [bocca, bollo, cheese_and_ham, veggie, marisol, four_cheese, curr_w_wo_smoked_salmon, arabiata,
                    green_pesto, red_pesto, potw]:
            mix_keuze.add_choice(Choice(name=prod.name))
            prod.add_choiceList(groote_keuze)
            prod.add_choiceList(pasta_keuze)
            prod.add_choiceList(toppings_keuze)
            products.add(prod)

        for prod in [mix_2, mix_3]:
            prod.add_choiceList(groote_keuze)
            prod.add_choiceList(pasta_keuze)
            prod.add_choiceList(toppings_keuze)
            prod.add_choiceList(mix_keuze.update_name(mix_keuze.name + " 1?"))
            prod.add_choiceList(mix_keuze.update_name(mix_keuze.name + " 2?"))

        products.add(mix_2)
        mix_3.add_choiceList(mix_keuze.update_name(mix_keuze.name + " 3?"))
        products.add(mix_3)

        left_x_lim = 650
        right_x_lim = width
        top_y_lim = height-270
        bottom_y_lim = 50
        extra_section = parse_pdf(local_file_path,
                                     coords=(left_x_lim, top_y_lim, right_x_lim, height - bottom_y_lim))
        lines = extra_section.split("\n")

        prod = Product(
            name=" ".join(lines[0].strip().split(" ")[:-1]),
            description="".join([lines[1].strip(), lines[2].strip()]),
            price=comma_float(lines[0].strip().split(" ")[-1])
        )
        prod.add_choiceList(toppings_keuze)
        products.add(prod)
        products.add(
            Product(
                name=" ".join(lines[4].strip().split(" ")[:-1]),
                description="".join([lines[5].strip()]).replace("€", "euro "),
                price=comma_float(lines[4].strip().split(" ")[-1])
            )
        )
        products.add(
            Product(
                name=" ".join(lines[6].strip().split(" ")[:-1]),
                price=comma_float(lines[6].strip().split(" ")[-1])
            )
        )
        products.add(
            Product(
                name=" ".join(lines[7].strip().split(" ")[:-1]),
                price=comma_float(lines[7].strip().split(" ")[-1])
            )
        )

        end_time = time.time()
        elapsed_time = end_time - start_time
        # Convert seconds to minutes and seconds
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"get_prices executed in {minutes} minute(s) and {seconds:.2f} second(s).")
        return products, locatie

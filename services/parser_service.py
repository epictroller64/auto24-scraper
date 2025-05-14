from bs4 import BeautifulSoup
from bs4.element import Tag
from structures import Auto24Listing, Pagination
import abc
import re

class Auto24ParserService:
    def __init__(self) -> None:
        pass

    def parse_vehicle_details(self, response_text: str, preview: Auto24Listing.ScrapedListingPreview):
        soup = BeautifulSoup(response_text)
        gallery_element = soup.select("#lightgallery a")
        images = [x.attrs.get('href', '') for x in gallery_element if x.attrs.get('href') is not None]
        type_element = soup.select_one(".field-liik td.field span.value")
        if not type_element:
            raise Exception("No type element found")
        type_value = type_element.text
        first_reg_element = soup.select_one("tr.field-month_and_year td.field .value")
        if not first_reg_element:
            raise Exception("No first reg element found")
        first_reg_text = first_reg_element.text

        color_element = soup.select_one("tr.field-varvus td.field .value")
        if not color_element:
            raise Exception("No first reg element found")
        color_element_text = color_element.text

        technical_details = self.parse_vehicle_specifications(soup)
        features = []
        for section in soup.select("div.equipment"):
            category_headings = section.select("h3.heading.full")
            feature_lists = section.select("ul.group.full")

            for heading, ul in zip(category_headings, feature_lists):
                category = heading.get_text(strip=True)
                for li in ul.select("li.item"):
                    item = li.get_text(strip=True)
                    features.append(Auto24Listing.Feature(key=category, value=item))

        original_country_element = soup.select_one("div.-brought_from b")
        original_country_text = original_country_element.text if original_country_element else ""

        location_text = ""

        inspection_until_element = soup.select_one("div.-status b")
        inspection_until_text = inspection_until_element.text if inspection_until_element else ""

        seller_name_elem = soup.select_one("address.section.seller h2")
        seller_name = seller_name_elem.text if seller_name_elem else ""

        description_elem = soup.select_one(".-user_other")
        desc_text = description_elem.text if description_elem else ""
        return Auto24Listing.ScrapedListing(
            preview=preview,
            images=images,
            seller_name=seller_name,
            type=type_value,
            first_reg=first_reg_text,
            color=color_element_text,
            technical_details=technical_details,
            features=features,
            location=location_text,
            original_country=original_country_text,
            inspection_until=inspection_until_text,
            description=desc_text
        )

    def parse_vehicle_specifications(self, soup: BeautifulSoup):
        flat_data = {}

        label_map = {
            "istekohti": "seats",
            "uste arv": "doors",
            "pikkus": "lenght",
            "laius": "width",
            "kõrgus": "height",
            "tühimass": "empty_mass",
            "täismass": "full_mass",
            "kandevõime": "carry_weight",
            "piduriga haagis": "trailer_with_brakes",
            "pidurita haagis": "trailer_without_brakes",
            "teljevahe": "wheelbase",
            "mootori maht": "engine_size",  # handled later to choose l or cm³
            "võimsus": "power",
            "tippkiirus": "max_speed",
            "co2 (nedc)": "co2",
            "kütus": "fuel",
            "- linnas": "fuel_consumption_city",
            "- maanteel": "fuel_consumption_highway",
            "- keskmine": "fuel_consumption_average",
            "sildade arv": "axels"
        }

        # Find all table rows
        rows = soup.select('tr.item')

        for row in rows:
            label = row.select_one('td.label')
            value = row.select_one('td.value')

            if label and value:
                raw_label = label.get_text(strip=True).lower().replace('\xa0', ' ')
                clean_label = re.sub(r'[:\s]+$', '', raw_label)

                mapped_field = label_map.get(clean_label)
                value_text = value.get_text(" ", strip=True).replace('\xa0', ' ')

                if not mapped_field or not value_text.strip():
                    continue

                # Handle specific fields
                if mapped_field == "engine_size" and "cm³" in value_text:
                    continue
                elif mapped_field == "engine_size" and "l" in value_text:
                    flat_data["engine_size"] = parse_float(value_text)
                elif mapped_field.startswith("kütusekulu"):
                    flat_data["consumption"] = Auto24Listing.Consumption(highway=0, city=0, average=0)
                elif "linnas" in raw_label:
                    city_consumption = parse_float(value_text)
                    flat_data["consumption"] = flat_data.get("consumption", Auto24Listing.Consumption(highway=0, city=0, average=0)).copy(update={"city": city_consumption})
                elif "maanteel" in raw_label:
                    city_consumption = parse_float(value_text)
                    flat_data["consumption"] = flat_data["consumption"].copy(update={"highway": city_consumption})
                elif "keskmine" in raw_label:
                    city_consumption = parse_float(value_text)
                    flat_data["consumption"] = flat_data["consumption"].copy(update={"average": city_consumption})
                elif mapped_field.startswith("kütus"):
                    flat_data[mapped_field] = value_text
                elif mapped_field:
                    if "km" in value_text or "kg" in value_text or "mm" in value_text:
                        flat_data[mapped_field] = parse_int(value_text)
                    elif "l" in value_text:
                        flat_data[mapped_field] = parse_float(value_text)
                    else:
                        flat_data[mapped_field] = parse_int(value_text)

        return Auto24Listing.TechnicalDetail(**flat_data)

    def parse_prelistings(self, response_text: str):
        soup = BeautifulSoup(response_text)
        cars_section_element = soup.select_one("#usedVehiclesSearchResult-flex")
        if not cars_section_element:
            raise Exception("no cars section element found")
        result_rows = cars_section_element.select(".result-row")

        found_listings:list[Auto24Listing.ScrapedListingPreview] = []

        for result in result_rows:
            link = result.select_one("a.row-link")
            if not link:
                raise Exception("No link found while parsing prelisting")
            link_text = link.text
            title_element = result.select_one("div.title a.main")
            if not title_element:
                raise Exception("No title element found while parsing prelisting")
            all_spans_in_title = title_element.select("span")
            mark = all_spans_in_title[0].text
            model = all_spans_in_title[1].text
            model_short = all_spans_in_title[2].text
            engine = all_spans_in_title[3].text
            year = result.select_one("span.year")
            if not year:
                raise Exception("No year element found while parsing prelisting")
            year_text = year.text
            extra_element = result.select_one("div.extra")
            if not extra_element:
                raise Exception("No extra element found while parsing prelisting")
            price = result.select_one("span.price")
            price = price.text if price else ""
            mileage = result.select_one("span.mileage")
            mileage = mileage.text if mileage else ""
            fuel = result.select_one("span.fuel.sm-none")
            fuel = fuel.text if fuel else ""
            transmission = result.select_one("span.transmission")
            transmission = transmission.text if transmission else ""
            bodytype = result.select_one("span.bodytype")
            bodytype= bodytype.text if bodytype else ""
            drive = result.select_one("span.drive")
            drive = drive.text if drive else ""
            listing =  Auto24Listing.ScrapedListingPreview(
                title=title_element.text,
                price=price,
                mileage=mileage,
                year=year_text,
                gearbox=transmission,
                body=bodytype,
                fuel_type=fuel,
                drive=drive,
                mark=mark,
                model=model,
                model_short=model_short,
                engine=engine,
                link=link_text)
            found_listings.append(listing)
        return found_listings

    def parse_pagination(self, response_text: str):
        soup = BeautifulSoup(response_text)
        range_element = soup.select_one("div.current-range span.label")
        if not range_element:
            raise Exception("No range element found")
        total_vehicles = range_element.select_one("strong")
        if not total_vehicles:
            raise Exception("Total vehicles not found")
        total_vehicles_count = int(total_vehicles.text)
        page_control_element = range_element.select_one(".page-cntr")
        if not page_control_element:
            raise Exception("No page control element found")

        page_control_element_text = page_control_element.text.replace("(", "").replace(")", "")
        splitted = page_control_element_text.split("/")

        current_page = int(splitted[0])
        max_page = int(splitted[1])

        return Pagination.Pagination(max_page=max_page, current_page=current_page, total_vehicles=total_vehicles_count)

def parse_int(text):
    return int(re.sub(r"[^\d]", "", text)) if text and re.search(r"\d", text) else None

def parse_float(text):
    return float(re.sub(r"[^\d.]", "", text.replace(",", "."))) if text and re.search(r"\d", text) else None

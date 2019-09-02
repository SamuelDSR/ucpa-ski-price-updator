import json

from selenium import webdriver
from selenium.webdriver import FirefoxOptions

options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

# search start url
start_url = "https://www.ucpa.com/activite/ski-alpin"
driver.get(start_url)

resort_urls = [
    x.find_element_by_tag_name("a").get_attribute("href")
    for x in driver.find_elements_by_css_selector(
        ".ucpa-Search-item.ucpa-Search-item--simple")
]


def get_products_by_resort(url):
    driver.get(url)
    product_grids = driver.find_elements_by_css_selector(
        "r-Grid.ucpa-Product-list")
    all_offers = []
    for grid in product_grids:
        offer = {}
        offer["url"] = grid.find_element_by_tag_name("a").get_attribute("href")
        offer_details = json.loads(
            grid.find_element_by_tag_name("a").get_attribute("analytics-data"))
        offer.update(offer_details)
        all_offers.append(offer)
    return all_offers


def get_sejours_by_product(product_url):
    driver.get(product_url)
    target_props = [
        "dispo", "price", "discount", "ville", "trans", "typetrans", "date",
        "article", "group-id"
    ]

    def parse_sejour(web_element):
        sejour_detail = {}
        for prop in target_props:
            sejour_detail[prop] = web_element.get_attribute(prop)

        sejour_detail["reduction"] = web_element.find_element_by_class_name(
            "ucpa-Sejour-result-date").get_attribute("data-reduc")
        sejour_detail["price_unity"] = web_element.find_element_by_class_name(
            "ucpa-Sejour-result-oldPrice").get_attribute("innerHTML")
        sejour_detail["duration"] = web_element.find_element_by_class_name(
            "ucpa-Sejour-result-during").get_attribute("innerHTML")
        return sejour_detail

    all_sejour_details = [
        parse_sejour(x)
        for x in driver.find_elements_by_css_selector("ucpa-Sejour-resultItem")
    ]
    return all_sejour_details

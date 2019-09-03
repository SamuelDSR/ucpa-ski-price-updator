import json

from selenium import webdriver
from selenium.webdriver import FirefoxOptions, ChromeOptions

#  options = FirefoxOptions()
options = ChromeOptions()
options.add_argument("--headless")
#  driver = webdriver.Firefox(options=options)
driver = webdriver.Chrome("./chromedriver", options=options)

# search start url
start_url = "https://www.ucpa.com/activite/ski-alpin"


def get_resort_url_list(start_url):
    driver.get(start_url)
    resort_webitems = driver.find_elements_by_css_selector(
        ".ucpa-Search-item.ucpa-Search-item--simple")
    urls = []
    for item in resort_webitems:
        elements = item.find_elements_by_tag_name("a")
        if elements:
            urls.append(elements[0].get_attribute("href"))
    return urls


def get_products_by_resort(url):
    driver.get(url)
    product_webitems = driver.find_elements_by_css_selector(
        ".r-Grid.ucpa-Product-list")
    all_products = []
    for grid in product_webitems:
        product = {}
        a_webelem = grid.find_elements_by_tag_name("a")
        if a_webelem:
            product["url"] = a_webelem[0].get_attribute("href")
            product_details = json.loads(
                a_webelem[0].get_attribute("analytics-data"))
            product.update(product_details)
            all_products.append(product)
    return all_products


def get_sejours_by_product(product_url):
    driver.get(product_url)
    target_props = [
        "dispo", "price", "discount", "ville", "trans", "typetrans", "date",
        "article", "group-id"
    ]

    def parse_sejour(web_element):
        sejour = {}
        for prop in target_props:
            sejour[prop] = web_element.get_attribute(prop)

        date_items = web_element.find_elements_by_class_name(
            "ucpa-Sejour-result-date")
        if date_items:
            sejour["reduction"] = date_items[0].get_attribute("data-reduc")

        price_unity_items = web_element.find_elements_by_class_name(
            "ucpa-Sejour-result-oldPrice")
        if price_unity_items:
            sejour["price_unity"] = price_unity_items[0].get_attribute("innerHTML")

        during_items = web_element.find_elements_by_class_name(
            "ucpa-Sejour-result-during")
        if during_items:
            sejour["duration"] = during_items[0].get_attribute("innerHTML")

        return sejour

    all_sejours = [
        parse_sejour(x) for x in driver.find_elements_by_css_selector(
            ".ucpa-Sejour-resultItem")
    ]
    return all_sejours


resort_urls = get_resort_url_list(start_url)
resort_urls = resort_urls[:2]
sejour_list = []
for url in resort_urls:
    for product in get_products_by_resort(url):
        sejs = get_sejours_by_product(product["url"])
        for s in sejs:
            s.update(product)
        sejour_list.extend(sejs)

json.dump(sejour_list, open("ucpa-offer-list.json", "w"))

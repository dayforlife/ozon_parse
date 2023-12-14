"""Важно чтобы питон версия была не выше 3.10"""
import csv
import glob
import json
import re
import requests
import undetected_chromedriver
import ssl
from bs4 import BeautifulSoup

import time

from selenium.webdriver.common.by import By


ssl._create_default_https_context = ssl._create_unverified_context

driver = undetected_chromedriver.Chrome()


URI = "https://www.ozon.ru/category/smartfony-15502/"


def get_source_code(URI, filename):
    """Получение чтмл страницы"""
    driver.get(URI)
    time.sleep(5)
    html = driver.page_source
    with open('pages/' + filename, 'w', encoding='utf-8') as f:
        f.write(html)


def get_links():
    """Все ссылки"""
    link_list = []
    links = driver.find_elements(By.CLASS_NAME, "i0w")

    for link in links:
        link = link.find_element(By.CLASS_NAME, "is5").get_attribute("href")

        '''
        # pattern = re.compile(r'https://www\.ozon\.ru/product(.*?)/\?')
        # match = re.search(pattern, link)
        # if match:
        #     extracted_value = match.group(1)
        # link_list.append(extracted_value)
        '''

        link_list.append(link)


    with open("links_on_products.txt", "a") as f:
        f.writelines("\n".join(link_list))


def get_product_links():
    with open('links_on_products.txt', 'r', encoding='utf-8') as f:
        return f.readlines()


def data_parsing(product: str, i):
    # url = 'https://www.ozon.ru/api/composer-api.bx/page/json/v2' \
    #       f'?url={product}'

    # url = f"{product}"

    dict_to_json = {
        f"product{i}": {
            "title": None,
            "price_with_card": None,
            "price_without_card": None,
            "seller": None,
            "data_character": None,
        }
    }

    driver.get(product)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    try:
        title_elem = soup.find("h1", class_="ol")
        title = title_elem.text if title_elem else " "
    # print(title)
    except Exception as e:
        title = " "

    try:
        price_with_card_elem = soup.find("div", class_="n1l").find("span", class_="l0n")
        price_with_card = price_with_card_elem.text if price_with_card_elem else " "
        if price_with_card == " ":
            price_with_card_elem = soup.find("div", class_="n1l").find("span", class_="nl9")
        price_with_card = price_with_card_elem.text if price_with_card_elem else " "
    except Exception as e:
        price_with_card = " "

    try:
        price_without_card_elem = soup.find("div", class_="n1l").find("span", class_="ln9")
        price_without_card = price_without_card_elem.text if price_without_card_elem else " "
        # print(price_with_card, price_without_card)
    except Exception as e:
        price_without_card = " "

    try:
        info_seller = soup.find("div", class_="qj8")
        seller = info_seller.text if info_seller else " "
        # print(seller)
    except Exception as e:
        seller = " "

    data_ = {}
    try:
        data_character = soup.find("div", class_="j0u").find_all("dl", class_="u3j")
        for d in data_character:
            key = d.find("span", class_="j3u").text.strip()
            value = d.find("dd", class_="ju3").text.strip()
            data_[key] = value
    except Exception as e:
        key = None
        value = None
        data_[key] = value
    # print(data_)

    dict_to_json[f"product{i}"]["title"] = title.strip()
    dict_to_json[f"product{i}"]["price_with_card"] = price_with_card.strip()
    dict_to_json[f"product{i}"]["price_without_card"] = price_without_card.strip()
    dict_to_json[f"product{i}"]["seller"] = seller.strip()
    dict_to_json[f"product{i}"]["data_character"] = data_

    # print(dict_to_json)
    return dict_to_json
    # elem = driver.find_element(By.TAG_NAME, "pre").get_attribute('innerHTML')
    # filename = filename + str(i) + '.html'
    # with open('products/' + filename, 'w', encoding='utf-8') as f:
    #     f.write(elem)

def write_to_json(dict_):
    with open("data.json", "a", encoding='utf-8') as outfile:
        json.dump(dict_, outfile, indent=4, ensure_ascii=False)


def get_products():
    return glob.glob('products/*.html')


def get_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
        return json.loads(data)


def parse_data(data):
    widgets = data.get('widgetStates')
    print(widgets)


def main():
    MAX_PAGE = 1
    i = 1
    while i <= MAX_PAGE:
        filename = f'page_' + str(i) + '.html'
        if i == 1:
            get_source_code(URI, filename)
        else:
            url_param = URI + '?page=' + str(i)
            get_source_code(url_param, filename)

        i += 1

    get_links()
    products = get_product_links()
    for i, product in enumerate(products, start=1):
        try:
            dict_to_json = data_parsing(product, i)
            write_to_json(dict_to_json)
        except Exception as e:
            print(e)

    # products = get_products()
    # for product in products:
    #     time.sleep(60)
    #     product_json = get_json(product)
    #     result = parse_data(product_json)



if __name__ == "__main__":
    main()

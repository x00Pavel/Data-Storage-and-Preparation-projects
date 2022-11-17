import csv
from time import sleep
from bs4 import BeautifulSoup
import requests


def parse_page(url):
    print(f"Parsing page {url}")
    result = requests.get(url, timeout=10)
    name, price = None, None
    assert result.status_code == 200, f"Status code is {result.status_code}"
    page = BeautifulSoup(result.text, "html.parser")
    product_details = page.find("div", {"class": "productDetails"})
    assert product_details, "Product details not found"
    name = product_details.find("h1", {"class": "productTitle"})["data-name"]
    assert name, "Name not found"
    price = product_details.find("span", {"class": "productPrice"})["data-price"]
    assert price, "Price not found"
    return (url, name, price)


def write_to_tsv(data):
    with open("tmp_data.tsv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerows(data)


def main(url_list):
    result = []
    for url in url_list:
        result.append(parse_page(url))
        print(f"Sleeping for 5 seconds")
        sleep(5)
    write_to_tsv(result)


if __name__ == '__main__':
    with open("tmp_urls.txt", "r", encoding="utf-8") as f:
        urls = f.read().splitlines()
    main(urls[:20])
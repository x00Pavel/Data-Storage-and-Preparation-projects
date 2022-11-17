import requests
from bs4 import BeautifulSoup
from logging import getLogger
from urllib.parse import urljoin


logger = getLogger(__name__)
base_url = "https://www.goldsmiths.co.uk"


def find_urls(page: BeautifulSoup):
    logger.info("Finding urls")
    elements = page.find("div", {"class": "gridBlock row"}).find_all("div", {"class": "productTile"})
    urls = []
    for e in elements:
        product_path = e.find("a")["href"].strip()
        assert product_path, 'Product path is empty'
        urls.append(urljoin(base_url, product_path))
    return urls


def get_urls():
    result = []
    for page_num in range(0, 8):
        logger.info(f"Getting page {page_num}")
        get_url = urljoin(base_url, f"/c/Watches/Mens-Watches?q=%3Arelevance&sort=relevance&page={page_num}")
        response = requests.get(get_url, timeout=10)
        result.extend(find_urls(BeautifulSoup(response.text, "html.parser")))
    return result


if __name__ == '__main__':
    urls = get_urls()
    with open("tmp_urls.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

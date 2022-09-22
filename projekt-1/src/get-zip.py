from cgitb import reset
import re
import requests
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import bs4
from dateutil.parser import parse
from os.path import basename

base_source_url = "https://portal.cisjr.cz"
base_source_path = f"{base_source_url}/pub/draha/celostatni/szdc/2022/"
base_path = Path("../data/")
base_path.mkdir(exist_ok=True)


def download_files():
    def worker(url):
        # Get list of file URLs in the directory
        sub_dir = Path(f"{base_path}/{url[1]}")
        sub_dir.mkdir(exist_ok=True)

        r = requests.get(url)
        assert r.ok, f"GET {url} failed with {r.status_code}"
        data = bs4.BeautifulSoup(r.text, "html.parser")

        # Download all files in a directory
        status_codes = []
        for l in data.find_all("a"):
            with urlopen(base_source_url + l["href"]) as f:
                zip_data = f.read()
            assert zip_data
            with open(Path(sub_dir, l["href"]).name, "wb") as zip_f:
                zip_f.write(zip_data)

            status_codes.append(r.status_code)
        return status_codes

    # Download content of source dir
    dir_content = requests.get(base_source_path)
    assert dir_content.ok, f"GET request for {base_source_path} is not successful"
    data_dir_content = bs4.BeautifulSoup(dir_content.text, "html.parser")
    
    # Get all dir links
    links = []
    for d in data_dir_content.find_all("a"):
        try:
            parse(d.text)
            links.append((f'{base_source_url}/{d["href"]}', d.text))
        except:
            print(f"Not a directory {d.text}")

    # Recursively download all from each directory
    print(links)
    with ThreadPoolExecutor(max_workers=10) as executor:
        result = executor.map(worker, links)

    return result


def unzip_files(files):
    ...


def main():
    files = download_files()
    unzip_files(files)


if __name__ == "__main__":
    main()
import requests
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import bs4
from dateutil.parser import parse
from subprocess import check_output
import logging
import sys

thread_log = logging.getLogger("thread_logger")
thread_log.setLevel("DEBUG")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
thread_log.addHandler(handler)


base_source_url = "https://portal.cisjr.cz"
base_source_path = f"{base_source_url}/pub/draha/celostatni/szdc/2022/"
parent_dir = Path(__file__).parent.absolute()
base_path = parent_dir.joinpath("data")
base_path.mkdir(exist_ok=True)

def unzip_files(dir: Path):
    """
    Unzip all files in a directory. Files are parsed GZIP compressed files with
    .zip extension. This implementation uses `gunzip` command line tool.

    :param dir: directory with files to unzip
    :type dir: pathlib.Path
    """
    for f in dir.iterdir():
        cmd = ["gunzip", "-S", ".zip"]
        check_output(cmd + [str(f)])
    thread_log.info(f"Unzipped all files in {dir}")


def download_files_in_dir(data: bs4.BeautifulSoup, dir: Path):
    """
    Download all files form a directory. Directory by itself has to be created
    before. Files are parsed from bs4.BeautifulSoup object using href attribute
    of <a> tag.

    :param data: HTML page with directory content
    :type data: bs4.BeautifulSoup
    :param dir: directory where to download files
    :type dir: pathlib.Path
    """

    thread_log.info(f"Downloading files to {dir}")
    for l in data.find_all("a"):
        if not l.text.endswith(".zip"): continue
        with urlopen(base_source_url + l["href"]) as f:
            zip_data = f.read()
        assert zip_data
        with dir.joinpath(l.text).open("wb") as zip_f:
            zip_f.write(zip_data)
            thread_log.info(f"Downloaded {l.text}")
    thread_log.info(f"Downloaded all files into {dir}")


def worker(url):
    """
    Worker function for ThreadPoolExecutor
    
    :param url: tuple of (url, dir_name)
    """
    # Get list of file URLs in the directory
    sub_dir = Path(f"{base_path}/{url[1]}")
    sub_dir.mkdir(exist_ok=True)

    r = requests.get(url[0])
    assert r.ok, f"GET {url[0]} failed with {r.status_code}"
    data = bs4.BeautifulSoup(r.text, "html.parser")

    # Download all files in a directory
    download_files_in_dir(data, sub_dir)
    thread_log.info(f"Finished processing {url[0]}")


def prepare_files():
    """
    Prepare files for further processing meaning download files and extract file
    from an archive. Implemented using multithreading.
    """
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

    # Recursively download all from each directory and gunzip it
    with ThreadPoolExecutor(max_workers=11) as executor:
        thread_log.info("Starting threads")
        executor.map(worker, links)
    for d in base_path.iterdir():
        unzip_files(d)
        

def main():
    prepare_files()


if __name__ == "__main__":
    main()
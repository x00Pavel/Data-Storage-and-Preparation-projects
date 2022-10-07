from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from subprocess import check_output
from urllib.request import urlopen

import bs4
import requests
from dateutil.parser import parse

from upaproject import data_base_path, thread_log

base_source_url = "https://portal.cisjr.cz"
base_source_path = f"{base_source_url}/pub/draha/celostatni/szdc/2022/"


class Downloader:
    @classmethod
    def unzip_files(cls, dir: Path):
        """
        Unzip all files in a directory. Files are parsed GZIP compressed files with
        .zip extension. This implementation uses `gunzip` command line tool.

        :param dir: directory with files to unzip
        :type dir: pathlib.Path
        """
        for f in dir.iterdir():
            if f.suffix != ".zip":
                continue
            cmd = ["gunzip", "-S", ".zip"]
            check_output(cmd + [str(f)])
        thread_log.info(f"Unzipped all files in {dir}")

    @classmethod
    def download_files_in_dir(cls, data: bs4.BeautifulSoup, dir: Path):
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
            if not l.text.endswith(".zip"):
                thread_log.warning(f"Skipping {l.text}: not a ZIP extension")
                continue
            dst = dir.joinpath(l.text)
            dst_xml = dir.joinpath(dst.stem)
            if dst.exists() and dst.stat().st_size > 0:
                thread_log.warning(f"Skipping {str(dst)}: ZIP already exists")
                continue
            elif dst_xml.exists() and dst_xml.stat().st_size > 0:
                thread_log.warning(f"Skipping {l.text}: XML already exists")
                continue
            
            with urlopen(base_source_url + l["href"]) as f:
                zip_data = f.read()
            assert zip_data, "No data downloaded"
            with dst.open("wb") as zip_f:
                zip_f.write(zip_data)
                thread_log.warning(f"Downloaded {dir}/{l.text}")
        thread_log.info(f"Downloaded all files into {dir}")

    @classmethod
    def worker(cls, url):
        """
        Worker function for ThreadPoolExecutor
        
        :param url: tuple of (url, dir_name)
        """
        # Get list of file URLs in the directory
        sub_dir = Path(f"{data_base_path}/{url[1]}")
        sub_dir.mkdir(exist_ok=True)

        r = requests.get(url[0])
        assert r.ok, f"GET {url[0]} failed with {r.status_code}"
        data = bs4.BeautifulSoup(r.text, "html.parser")

        # Download all files in a directory
        cls.download_files_in_dir(data, sub_dir)
        thread_log.info(f"Finished processing {url[0]}")

    @classmethod
    def prepare_files(cls):
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
            executor.map(cls.worker, links)
        for d in data_base_path.iterdir():
            Downloader.unzip_files(d)
    
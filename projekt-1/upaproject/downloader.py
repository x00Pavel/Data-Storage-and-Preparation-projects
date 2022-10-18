from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from subprocess import check_output
from urllib.request import urlopen

import bs4
import requests

from upaproject import data_base_path, default_logger as logger

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
        logger.info(f"Unzipped all files in {dir}")

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
        logger.info(f"Downloading files to {dir}")
        for l in data.find_all("a"):
            if not l.text.endswith(".zip"):
                logger.debug(f"Skipping {l.text}: not a ZIP extension")
                continue
            dst = dir.joinpath(l.text)
            dst_xml = dir.joinpath(dst.stem)
            if dst.exists() and dst.stat().st_size > 0:
                logger.debug(f"Skipping {str(dst)}: ZIP already exists")
                continue
            elif dst_xml.exists() and dst_xml.stat().st_size > 0:
                logger.debug(f"Skipping {l.text}: XML already exists")
                continue
            
            with urlopen(base_source_url + l["href"]) as f:
                zip_data = f.read()
            assert zip_data, "No data downloaded"
            with dst.open("wb") as zip_f:
                zip_f.write(zip_data)
                logger.debug(f"Downloaded {dir}/{l.text}")
        logger.warning(f"Downloaded all files into {dir}")

    @classmethod
    def worker(cls, url):
        """
        Worker function for ThreadPoolExecutor
        
        :param url: tuple of (url, dir_name)
        """
        # Get list of file URLs in the directory
        sub_dir = Path(f"{data_base_path}/{url[1]}")
        sub_dir.mkdir(exist_ok=True)

        if url[0].endswith(".zip"):
            logger.debug(f"Downloading single ZIP file {url[0]}")
            dst = sub_dir.joinpath(url[0].split("/")[-1])
            with urlopen(url[0]) as f:
                zip_data = f.read()
            assert zip_data, "No data downloaded"
            with dst.open("wb") as zip_f:
                zip_f.write(zip_data)
            check_output(["unzip", "-o", str(dst), "-d", str(sub_dir)], encoding="utf-8")
            logger.debug(f"Downloaded {dst}")
        else:
            r = requests.get(url[0])
            assert r.ok, f"GET {url[0]} failed with {r.status_code}"
            data = bs4.BeautifulSoup(r.text, "html.parser")

            # Download all files in a directory
            cls.download_files_in_dir(data, sub_dir)
            Downloader.unzip_files(sub_dir)
            logger.debug(f"Finished processing {url[0]}")

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
        allowed_links = ('2021-12', '2022-01', '2022-02', '2022-03', '2022-04',
                         '2022-05', '2022-06', '2022-07','2022-08', '2022-09',
                         '2022-10', 'GVD2022.zip')
        for d in data_dir_content.find_all("a"):
            try:
                logger.debug(d.text)
                if d.text not in allowed_links:
                    logger.warning(f"Directory is not allowed {d.text}")
                    continue
                links.append((f'{base_source_url}/{d["href"]}', d.text))
            except:
                logger.warning(f"Not a directory {d.text}")
        # Recursively download all from each directory and gunzip it
        with ThreadPoolExecutor(max_workers=11) as executor:
            logger.info("Starting threads")
            executor.map(cls.worker, links)
    
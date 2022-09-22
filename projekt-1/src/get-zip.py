import requests
import threading


base_url = "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/"
base_path = "../data/"

def download_files():
    def worker(url, path):
        ...
    ...

def unzip_files(files):
    ...

def main():
    files = download_files()
    unzip_files(files)

if __name__ == "__main__":
    main()
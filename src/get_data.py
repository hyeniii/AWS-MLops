from pathlib import Path
import src.acquire_data.download_unzip as du
from urllib.error import *
import py7zr

def download_data(url: str, output_path: Path) -> None:
    """
    Downloads the file at the url to the directory 'output_path'.
    -------------------------------------------------------------
    Arguments:
    1. url: The URL link from which data is to be acquired
    2. output_path: The directory to which data is stored
    """
    try:
        du.download_unzip(url, output_path)
        print("Downloaded successfully.")
    except URLError as e:
        print(f"URL Error in get_data.download_data: {e}.")
    except Exception as e:
        print(f"An unexpected error occurred in get_data.download_data: {e}.")

def unzip_file(zipfile_path: Path, dataset_path: Path) -> None:
    """
    Unzips the file previously extracted.
    -------------------------------------------------------------
    Arguments:
    1. zipfile_path: The file path to compressed file which is to be extracted
    2. dataset_path: The directory to which extracted data is stored
    """
    try:
        with py7zr.SevenZipFile(zipfile_path, mode='r') as archive:
            # Extract all the contents to the specified directory
            archive.extractall(dataset_path)
            print("The file extraction was successful.")
    except py7zr.Bad7zFile as e:
        print(f"Bad 7z File in get_data.unzip_file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in get_data.unzip_file: {e}")
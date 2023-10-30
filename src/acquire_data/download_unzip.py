import os
import src.acquire_data.download_file as df
import zipfile

def download_unzip(url: str, dataset_path: str):
    """
    Downloads the file at the specified 'url' and unzips it
    at the specified 'dataset_path'.
    """
    filename_zip = 'data.zip'
    file_path_zip = os.path.join(dataset_path, filename_zip)
    fresh_download = df.download_file(url, dataset_path, filename_zip)
    if fresh_download:
        # TODO This naively assumes downloaded implies extracted
        zf = zipfile.ZipFile(file_path_zip)
        zf.extractall(dataset_path)
import os
from urllib import request

def download_file(url, dataset_path, filename):
    """
    Downloads the file at the url to the path 'dataset_path/filename'.

    Returns True if dataset was downloaded, False if already existing
    """
    os.makedirs(dataset_path, exist_ok=True)
    file_path = os.path.join(dataset_path, filename)
    if not os.path.exists(file_path):
        request.urlretrieve(url, file_path)
        return True
    else:
        return False
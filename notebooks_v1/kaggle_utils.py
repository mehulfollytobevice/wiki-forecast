import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

def unzip_file(zip_file_path, target_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
    os.remove(zip_file_path)


def download_data(competition_name):
    directory = os.path.dirname(os.path.abspath(__file__))
    competition_folder = os.path.join(directory, 'data', competition_name)

    if not os.path.exists(competition_folder):
        os.makedirs(competition_folder)

    api = KaggleApi()
    api.authenticate()

    zip_file_path = os.path.join(competition_folder, f'{competition_name}.zip')
    api.competition_download_files(competition_name, path=competition_folder)

    unzip_file(zip_file_path, competition_folder)

    file_paths = []
    for root, dirs, files in os.walk(competition_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(os.path.abspath(file_path))

    return file_paths

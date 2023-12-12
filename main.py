import configparser
import asyncio
from seedr_client import SeedrClient
from processed_file_registry import ProcessedFileRegistry
from media_bridge_manager import MediaBridgeManager

class MediaBridgeConfiguration():
    def __init__(
            self, 
            seedr_movies_folder_name: str, 
            seedr_series_folder_name: str, 
            movies_storage_path: str,
            series_storage_path: str,
    ):
        self.seedr_movies_folder_name = seedr_movies_folder_name
        self.seedr_series_folder_name = seedr_series_folder_name
        self.movies_storage_path = movies_storage_path
        self.series_storage_path = series_storage_path

class Credentials:
    def __init__(
            self, 
            seedr_username: str, 
            seedr_password: str,
    ):
        self.seedr_username = seedr_username
        self.seedr_password = seedr_password

'''
Reads credentials as configured in credentials.ini in the root directory.
'''
def get_credentials(config_parser: configparser) -> Credentials:
    credential_file_path = 'credentials.ini'
    config_parser.read(credential_file_path)

    seedr_section = 'Seedr'
    seedr_user = config_parser.get(seedr_section, 'username')
    seedr_password = config_parser.get(seedr_section, 'password')

    return Credentials(
        seedr_username=seedr_user, 
        seedr_password=seedr_password,
    )

'''
Reads the app configuration as configured in config.ini in the root directory.
'''
def get_configuration(config_parser: configparser) -> MediaBridgeConfiguration:
    config_file_path = 'config.ini'
    config_parser.read(config_file_path)

    basic_section = 'Basic'
    seedr_movies_folder_name = config_parser.get(basic_section, 'seedr_movies_folder_name')
    seedr_series_folder_name = config_parser.get(basic_section, 'seedr_series_folder_name')
    movies_storage_path = config_parser.get(basic_section, 'movies_storage_path')
    series_storage_path = config_parser.get(basic_section, 'series_storage_path')

    return MediaBridgeConfiguration(
        seedr_movies_folder_name=seedr_movies_folder_name,
        seedr_series_folder_name=seedr_series_folder_name,
        movies_storage_path=movies_storage_path,
        series_storage_path=series_storage_path,
    )

'''
Finds a seedr folder ID by its name

If no folder with the input name exists, an Exception is raised.
'''
def get_seedr_folder_id_by_name(seedr_client: SeedrClient, expected_folder_name: str) -> int:
    seedr_root_folder_contents = seedr_client.list_root_contents()
    res = __get_seedr_folder_id_by_name_helper(
        seedr_client=seedr_client, 
        expected_folder_name=expected_folder_name,
        folder_contents=seedr_root_folder_contents,
    )
    if res != None:
        return res
    else:
        raise Exception(f"Did not find folder named {expected_folder_name} in seedr")

'''
Finds a folder by its name

Does this recursively, scanning first root folders then all subfolders
of the checked folders
'''
def __get_seedr_folder_id_by_name_helper(
        seedr_client: SeedrClient, 
        expected_folder_name: str, 
        folder_contents: any,
) -> (int, None):
    for folder in folder_contents['folders']:
        folder_name = folder['name']
        if folder_name == expected_folder_name:
            return folder['id']
        elif not expected_folder_name.startswith(folder_name):
            continue

        child_folder_contents = seedr_client.list_folder_contents(folder['id'])
        response = __get_seedr_folder_id_by_name_helper(
            seedr_client=seedr_client,
            expected_folder_name=expected_folder_name,
            folder_contents=child_folder_contents,
        )
        if response != None:
            return response
    return None

async def perform_movie_series_scan(
        manager: MediaBridgeManager, 
        seedr_series_folder_id: int, 
        series_storage_path: str,
        seedr_movies_folder_id: int,
        movies_storage_path: str,
):
    manager.scan(folder_id=seedr_series_folder_id, base_download_path=series_storage_path)
    manager.scan(folder_id=seedr_movies_folder_id, base_download_path=movies_storage_path)
    

async def main():
    print("initializing...")

    config_parser = configparser.ConfigParser()
    credentials = get_credentials(config_parser=config_parser)
    configuration = get_configuration(config_parser=config_parser)

    seedr_client = SeedrClient(credentials.seedr_username, credentials.seedr_password)
    registry = ProcessedFileRegistry(registry_file_path="processed_registry.txt")

    bridgeManager = MediaBridgeManager(
        seedr_client=seedr_client, 
        processed_file_registry=registry,
    )

    series_folder_id = get_seedr_folder_id_by_name(
        seedr_client=seedr_client,
        expected_folder_name=configuration.seedr_series_folder_name,
    )
    movies_folder_id = get_seedr_folder_id_by_name(
        seedr_client=seedr_client,
        expected_folder_name=configuration.seedr_movies_folder_name,
    )
    print("Finished initializing.")

    print("Starting scans.")
    while True:
        await bridgeManager.scan(
            folder_id=series_folder_id,
            base_download_path=configuration.series_storage_path, 
            folder_name=configuration.seedr_series_folder_name,
        )
        await bridgeManager.scan(
            folder_id=movies_folder_id,
            base_download_path=configuration.movies_storage_path,
            folder_name=configuration.seedr_movies_folder_name,
        )
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())

import configparser
import asyncio
from seedr_client import SeedrClient
from processed_file_registry import ProcessedFileRegistry
from media_bridge_manager import MediaBridgeManager

class MediaBridgeConfiguration():
    def __init__(
            self, 
            seedr_movies_prefix_name: str, 
            seedr_series_prefix_name: str, 
            movies_storage_path: str,
            series_storage_path: str,
    ):
        self.seedr_movies_prefix_name = seedr_movies_prefix_name
        self.seedr_series_prefix_name = seedr_series_prefix_name
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
    seedr_movies_prefix_name = config_parser.get(basic_section, 'seedr_movies_prefix_name')
    seedr_series_prefix_name = config_parser.get(basic_section, 'seedr_series_prefix_name')
    movies_storage_path = config_parser.get(basic_section, 'movies_storage_path')
    series_storage_path = config_parser.get(basic_section, 'series_storage_path')

    return MediaBridgeConfiguration(
        seedr_movies_prefix_name=seedr_movies_prefix_name,
        seedr_series_prefix_name=seedr_series_prefix_name,
        movies_storage_path=movies_storage_path,
        series_storage_path=series_storage_path,
    )

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

    print("Finished initializing.")

    print("Starting scans.")
    while True:
        try:
            await bridgeManager.scan(
                base_download_path=configuration.series_storage_path, 
                scan_prefix=configuration.seedr_series_prefix_name,
            )
            await bridgeManager.scan(
                base_download_path=configuration.movies_storage_path,
                scan_prefix=configuration.seedr_movies_prefix_name,
            )
        except Exception as e:
            print(e)
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())

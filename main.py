import configparser
from seedr_client import SeedrClient, SeedrCredentials
from processed_file_registry import ProcessedFileRegistry
from media_bridge_manager import MediaBridgeManager

class MediaBridgeConfiguration():
    def __init__(self, media_bridge_folder_name: str, download_base_path: str):
        self.media_bridge_folder_name = media_bridge_folder_name
        self.download_base_path = download_base_path

'''
Returns a SeedrCredentials object.
Reads credentials from credentials.ini in the root directory
'''
def get_seedr_credentials(config_parser: configparser) -> SeedrCredentials:
    credential_file_path = 'credentials.ini'
    config_parser.read(credential_file_path)

    credentials_auth_section = 'Authentication'

    user = config_parser.get(credentials_auth_section, 'seedr_username')
    password = config_parser.get(credentials_auth_section, 'seedr_password')
    return SeedrCredentials(username=user, password=password)

def get_configuration(config_parser: configparser) -> MediaBridgeConfiguration:
    config_file_path = 'config.ini'
    config_parser.read(config_file_path)

    config_seedr_section = 'Seedr Config'

    media_bridge_folder_name = config_parser.get(config_seedr_section, 'seedr_media_bridge_folder_name')
    download_base_path = config_parser.get(config_seedr_section, 'download_base_path')
    return MediaBridgeConfiguration(
        media_bridge_folder_name=media_bridge_folder_name, 
        download_base_path=download_base_path,
    )

def get_media_bridge_seedr_folder_id(seedr_client: SeedrClient, expected_folder_name: str) -> int:
    seedr_root_folder_contents = seedr_client.list_root_contents()
    for folder in seedr_root_folder_contents['folders']:
        if folder['name'] == expected_folder_name:
            return folder['id']
    raise Exception(f"Did not find folder named ${expected_folder_name} in root seedr directory")

def main():
    config_parser = configparser.ConfigParser()
    credentials = get_seedr_credentials(config_parser=config_parser)
    configuration = get_configuration(config_parser=config_parser)

    seedr_client = SeedrClient(credentials.username, credentials.password)
    registry = ProcessedFileRegistry(registry_file_path="processed_registry.txt")
    bridgeManager = MediaBridgeManager(
        seedr_client=seedr_client, 
        processed_file_registry=registry, 
        download_base_path=configuration.download_base_path,
    )

    media_bridge_seedr_folder_id = get_media_bridge_seedr_folder_id(
        seedr_client=seedr_client,
        expected_folder_name=configuration.media_bridge_folder_name,
    )
    bridgeManager.scan(folder_id=media_bridge_seedr_folder_id)

if __name__ == "__main__":
    main()

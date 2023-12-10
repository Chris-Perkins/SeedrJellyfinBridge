import configparser
from seedr_client import SeedrClient, SeedrCredentials
from processed_file_registry import ProcessedFileRegistry
from media_bridge_manager import MediaBridgeManager

class SeedrCredentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

'''
Returns a SeedrCredentials object.
Reads credentials from credentials.ini in the root directory
'''
def get_seedr_credentials(config_parser):
    credential_file_path = 'credentials.ini'
    config_parser.read(credential_file_path)

    credentials_auth_section = 'Authentication'

    user = config_parser.get(credentials_auth_section, 'seedr_username')
    password = config_parser.get(credentials_auth_section, 'seedr_password')
    return SeedrCredentials(username=user, password=password)

def main():
    config = configparser.ConfigParser()
    credentials = get_seedr_credentials(config_parser=config)
    seedr_client = SeedrClient(credentials.username, credentials.password)
    registry = ProcessedFileRegistry(registry_file_path="processed_registry.txt")
    bridgeManager = MediaBridgeManager(seedr_client=seedr_client, processed_file_registry=registry)

    bridgeManager.scan()

if __name__ == "__main__":
    main()
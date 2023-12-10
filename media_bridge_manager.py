from seedr_client import SeedrClient
from processed_file_registry import ProcessedFileRegistry

class MediaBridgeManager():
    def __init__(self, seedr_client: SeedrClient, processed_file_registry: ProcessedFileRegistry) -> None:
        self.seedr_client = seedr_client
    
    def scan(self):
        pass

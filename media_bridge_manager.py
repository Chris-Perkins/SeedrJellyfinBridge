import os
from seedr_client import SeedrClient
from processed_file_registry import ProcessedFileRegistry
from jellyfin_client import JellyfinClient

'''
The bridge between Seedr, the local system, and jellyfin.

Scans seedr for new files.
New files are then downloaded to a file path used Jellyfin.
After download, refresh Jellyfin's library so it shows up appropriately.

What could be cool: Hook this back up to Discord; post a message in a channel
after the movie is done downloading
'''
class MediaBridgeManager():

    def __init__(self, 
                 seedr_client: SeedrClient, 
                 processed_file_registry: ProcessedFileRegistry,
                 jellyfin_client: JellyfinClient,
    ) -> None:
        self.seedr_client = seedr_client
        self.processed_file_registry = processed_file_registry
        self.jellyfin_client = jellyfin_client
    
    '''
    Scans the input folder_id for any new files. New files are uploaded to
    the specified base download path, postfixed by their location in seedr.

    After scanning, the catalog is refreshed.
    That's a little wasteful, but whatever.
    '''
    async def scan(self, folder_id: int, base_download_path: str):
        folder_contents = self.seedr_client.list_folder_contents(folder_id=folder_id)
        self.__recursively_process_seedr_folder(folder_contents, base_download_path)
        self.jellyfin_client.refresh_catalog()
    
    '''
    Recursively processes the input folder contents, including all children
    folders.

    A file is processed once the contents of the folder have been downloaded,
    and marked in the registry as processed.

    If a folder or file is already present in the registry and has not been
    updated since it was added to the registry, it is skipped
    such that an object will only ever be processed once.

    After a folder has been processed, it is deleted to save storage.
    '''
    def __recursively_process_seedr_folder(self, folder_contents: any, base_download_path: str, cur_path: str = ""):
        for folder in folder_contents['folders']:
            folder_id = folder['id']
            folder_name = folder['name']
            timestamp = folder['last_update']
            
            if self.processed_file_registry.is_processed(folder_id, timestamp):
                continue

            print(f"Scanning {folder}")
            child_folder_contents = self.seedr_client.list_folder_contents(folder_id)
            # for some reason, a folder name includes the name of parent folders
            # so we don't need to keep a track of the path manually
            self.__recursively_process_seedr_folder(
                folder_contents=child_folder_contents, 
                base_download_path=base_download_path, 
                cur_path=folder_name,
            )
            self.processed_file_registry.mark_processed(item_id=folder_id, timestamp=timestamp)
            self.seedr_client.delete_folder(folder_id=folder_id)
            print(f"Finished scanning and deleted {folder}")

        for file in folder_contents['files']:
            file_name = file['name']
            valid_cur_path = cur_path.replace("\"", "").split("/")

            output_path = os.path.join(base_download_path, valid_cur_path[-1], file_name)
            print(output_path)
            self.seedr_client.download_file(
                file_id=file['id'], 
                destination_path=output_path,
            )
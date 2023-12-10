import os
from seedr_client import SeedrClient
from processed_file_registry import ProcessedFileRegistry

class MediaBridgeManager():

    def __init__(self, 
                 seedr_client: SeedrClient, 
                 processed_file_registry: ProcessedFileRegistry,
                 download_base_path: str
    ) -> None:
        self.seedr_client = seedr_client
        self.processed_file_registry = processed_file_registry
        self.download_base_path = download_base_path
    
    def scan(self, folder_id):
        folder_contents = self.seedr_client.list_folder_contents(folder_id=folder_id)
        self.__recursively_process_seedr_folder(folder_contents)
    
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
    def __recursively_process_seedr_folder(self, folder_contents: any, cur_path: str = ""):
        for folder in folder_contents['folders']:
            print(folder)
            folder_id = folder['id']
            folder_name = folder['name']
            timestamp = folder['last_update']
            
            # if self.processed_file_registry.is_processed(folder_id, timestamp):
            #     pass

            child_folder_contents = self.seedr_client.list_folder_contents(folder_id)
            # for some reason, a folder name includes the name of parent folders
            # so we don't need to keep a track of the parents themselves
            self.__recursively_process_seedr_folder(folder_contents=child_folder_contents, cur_path=folder_name)

            self.processed_file_registry.mark_processed(item_id=folder_id, timestamp=timestamp)

        for file in folder_contents['files']:
            file_name = file['name']
            valid_cur_path = cur_path.replace("\"", "").replace("/", "\\")

            output_path = os.path.join(self.download_base_path, valid_cur_path, file_name)
            print(output_path)
            self.seedr_client.download_file(
                file_id=file['id'], 
                destination_path=output_path,
            )
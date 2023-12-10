'''
ProcessedFileRegistry keeps track of what objects have already been processed,
using a combination of item IDs and last updated timestamps.

You can use this to query if an object has already been processed, so an object
is only processed fully once.
'''
class ProcessedFileRegistry:
    def __init__(self, registry_file_path = "registry"):
        self.registry = set()
        self.registry_file_path = registry_file_path
        self.__read_registry_from_file(file_path=self.registry_file_path)

    def mark_processed(self, item_id, timestamp):
        unique_entry = self.__create_entry_key(item_id, timestamp)
        self.registry.add(unique_entry)
        self.__save_registry_to_file(file_path=self.registry_file_path)
        self.__read_registry_from_file(file_path=self.registry_file_path)

    def is_processed(self, item_id, timestamp):
        unique_entry = self.__create_entry_key(item_id, timestamp)
        return unique_entry in self.registry

    def __read_registry_from_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.registry = set(line.strip() for line in file)
        except FileNotFoundError:
            print(f"File '{file_path}' not found. Starting with an empty registry.")

    def __save_registry_to_file(self, file_path):
        with open(file_path, "w") as file:
            file.write("\n".join(self.registry))
    
    def __create_entry_key(self, item_id: str, timestamp: str) -> str:
        return f"{item_id}_{timestamp}"

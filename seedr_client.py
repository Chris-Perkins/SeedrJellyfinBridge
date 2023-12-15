import requests
import os

# Client based on the Seedr API V1 client documented here:
# https://www.seedr.cc/docs/api/rest/v1
class SeedrClient():
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    

    def list_root_contents(self) -> any:
        url = "https://www.seedr.cc/rest/folder"
        response = requests.get(url, auth=(self.username, self.password))

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)
    

    def list_folder_contents(self, folder_id: int) -> any:
        url = "https://www.seedr.cc/rest/folder/{folder_id}"
        response = requests.get(url.format(folder_id=folder_id), auth=(self.username, self.password))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)


    # 1048576 represents 1 megabyte; so we download in batches of 50 megabytes at a time.
    def download_file(self, file_id: int, destination_path: str, file_size: int, batch_size: int = 1_048_576 * 50) -> any:
        url = "https://www.seedr.cc/rest/file/{file_id}"
        directory = os.path.dirname(destination_path)
        os.makedirs(directory, exist_ok=True)

        with open(destination_path, "wb") as file:
            for start in range(0, file_size, batch_size):
                end = min(start + batch_size - 1, file_size - 1)
                headers = {'Range': f'bytes={start}-{end}'}
                response = requests.get(url.format(file_id=file_id), auth=(self.username, self.password), headers=headers)

                if response.status_code == 206:
                    print("{:.10f}".format(start/file_size))
                    file.write(response.content)
                else:
                    raise Exception(f"Failed to download batch: {response.status_code}")


    def delete_folder(self, folder_id: int) -> any:
        url = "https://www.seedr.cc/rest/folder/{folder_id}"
        response = requests.delete(url.format(folder_id=folder_id), auth=(self.username, self.password))

        if response.status_code != 200:
            raise Exception(response)

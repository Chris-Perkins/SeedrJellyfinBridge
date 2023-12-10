import requests

class SeedrCredentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Client based on the Seedr API V1 client documented here:
# https://www.seedr.cc/docs/api/rest/v1
class SeedrClient():
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def list_root_contents(self):
        url = "https://www.seedr.cc/rest/folder"
        response = requests.get(url, auth=(self.username, self.password))

        if response.status_code == 200:
            print(response.json())
        else:
            raise response
    
    def list_folder_contents(self, folder_id):
        url = "https://www.seedr.cc/rest/folder/{folder_id}"
        response = requests.get(url.format(folder_id=folder_id), auth=(self.username, self.password))
        if response.status_code == 200:
            print(response.json())
        else:
            # Handle error
            raise response
        
    def download_file(self, file_id, destination_path):
        url = "https://www.seedr.cc/rest/file/{file_id}"
        response = requests.get(url.format(file_id=file_id), auth=(self.username, self.password))
        if response.status_code == 200:
            with open(destination_path, "wb") as file:
                file.write(response.content)
            print("File downloaded successfully.")
        else:
            raise response


    def delete_folder(self, folder_id):
        url = "https://www.seedr.cc/rest/folder/{folder_id}/delete"
        response = requests.post(url.format(folder_id=folder_id), auth=(self.username, self.password))

        if response.status_code == 200:
            print("File deleted successfully.")
        else:
            raise response

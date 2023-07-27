import os
from webdav3.client import Client


def synchronize_webdav_to_local(source_url, username, password, folders_to_download, local_destination):
    # WebDAV server URL and authentication credentials
    options = {
        "webdav_hostname": source_url,
        "webdav_login": username,
        "webdav_password": password,
        "timeout": 60
        # "verify": False
    }

    client = Client(options)
    client.verify = False  # Ignore SSL certificate

    for folder in folders_to_download:
        # Create a local folder to store the files from the current remote folder
        destination_folder = os.path.join(local_destination, os.path.basename(folder))
        os.makedirs(destination_folder, exist_ok=True)

        # Get the list of files in the remote folder
        remote_files = client.list(remote_path=folder)

        # Compare with the list of files in the local folder
        local_files = set(os.listdir(destination_folder))

        # Find new or modified files
        new_or_modified_files = [file for file in remote_files[1:] if file not in local_files]

        print()

        # Download new or modified files
        for file in new_or_modified_files:
            local_file_path = os.path.join(destination_folder, file)
            client.download_sync(remote_path=os.path.join(folder, file), local_path=local_file_path)

    print("Download completed!")


if __name__ == "__main__":
    # WebDAV server URL and authentication credentials
    source_url = 'https://raumschiff.cloud/nextcloud/remote.php/dav/files/delberin/eCallisto/bursts/'
    username = 'delberin.ali@fhnw.ch'
    password = 'Raum5ch1ff$Secur3'

    folders_to_download = ["type_I/", "type_II/", "type_III/", "type_IV/", "type_V/"]

    # Destination directory
    local_destination = "C:/Users/delbe/OneDrive - FHNW/Sync_Burst/"

    synchronize_webdav_to_local(source_url, username, password, folders_to_download, local_destination)

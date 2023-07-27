import os
import paramiko


def sync_local_to_server(local_folder, server_folder, hostname, port, username, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the server
        ssh.connect(hostname, port, username, password)
        sftp = ssh.open_sftp()

        sync_folders(local_folder, server_folder, sftp)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sftp.close()
        ssh.close()


def sync_folders(local_folder, server_folder, sftp):
    # List local files and folders
    local_items = os.listdir(local_folder)

    for item_name in local_items:
        local_item_path = os.path.join(local_folder, item_name)
        server_item_path = os.path.join(server_folder, item_name)

        if os.path.isdir(local_item_path):
            # If the item is a subfolder, recursively sync it
            try:
                sftp.mkdir(server_item_path)  # Create the folder on the server
                print(f"Created folder: {server_item_path}")
            except IOError:
                # The folder already exists on the server
                pass

            # Recursively sync the subfolder
            sync_folders(local_item_path, server_item_path, sftp)
        else:
            # If the item is a file, upload it to the server
            if item_name not in sftp.listdir(server_folder):
                sftp.put(local_item_path, server_item_path)
                print(f"Uploaded: {server_item_path}")


local_folder = "C:/Users/delbe/OneDrive - FHNW/Sync_Burst/"
server_folder = "/data/radio/Bursts/"
hostname = "10.35.147.65"
port = 22  # Default SSH port
username = "delberin"
password = "delberinali1992"

sync_local_to_server(local_folder, server_folder, hostname, port, username, password)

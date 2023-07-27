import os
import paramiko


def upload_folder(local_folder, remote_folder, hostname, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname, username=username, password=password)
        sftp_client = ssh_client.open_sftp()

        # Ensure the remote folder exists
        try:
            sftp_client.stat(remote_folder)
        except FileNotFoundError:
            sftp_client.mkdir(remote_folder)

        for root, dirs, files in os.walk(local_folder):
            relative_path = os.path.relpath(root, local_folder)
            remote_path = os.path.join(remote_folder, relative_path)

            # Create the remote directory if it doesn't exist
            try:
                sftp_client.stat(remote_path)
            except FileNotFoundError:
                sftp_client.mkdir(remote_path)

            for file in files:
                local_file_path = os.path.join(root, file)
                remote_file_path = os.path.join(remote_path, file)

                # Check if the file exists on the remote server
                try:
                    sftp_client.stat(remote_file_path)
                except FileNotFoundError:
                    print(f"Uploading {local_file_path} to {remote_file_path}")
                    sftp_client.put(local_file_path, remote_file_path)

        print("Upload completed successfully!")
        sftp_client.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh_client.close()


if __name__ == "__main__":
    local_folder_path = "C:/Users/delbe/OneDrive - FHNW/Sync_Burst/"
    remote_folder_path = "/data/radio/Bursts/"
    server_hostname = "10.35.147.65"
    server_username = "delberin"
    server_password = "delberinali1992"
    upload_folder(local_folder_path, remote_folder_path, server_hostname, server_username, server_password)
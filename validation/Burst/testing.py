import subprocess


def sync_files_between_servers(source_server, source_user, source_path, destination_server, destination_user, destination_path, ssh_port=22):
    rsync_command = f"rsync -avz -e 'ssh -p {ssh_port}' {source_user}@{source_server}:{source_path}/ {destination_user}@{destination_server}:{destination_path}/"

    try:
        subprocess.run(rsync_command, shell=True, check=True)
        print("File synchronization completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during synchronization: {e}")


if __name__ == "__main__":
    source_server = "SOURCE_SERVER_IP_OR_HOSTNAME"
    source_user = "SOURCE_SERVER_USERNAME"
    source_path = "/path/to/source_directory"

    destination_server = "10.35.147.65"
    destination_user = "delberin"
    destination_path = "/data/radio/Bursts/"

    ssh_port = 22  # Replace with the SSH port number if different from the default (22)

    sync_files_between_servers(source_server, source_user, source_path, destination_server, destination_user, destination_path, ssh_port)

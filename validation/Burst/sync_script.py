import os
from webdav3.client import Client

# WebDAV server URL and authentication credentials
source_url = 'https://raumschiff.cloud/nextcloud/remote.php/dav/files/delberin/eCallisto/bursts/'
username = 'delberin.ali@fhnw.ch'
password = 'Raum5ch1ff$Secur3'

options = {
    "webdav_hostname": source_url,
    "webdav_login": username,
    "webdav_password": password,
    # "verify": False  # Ignore SSL certificate verification for self-signed certificates
}

client = Client(options)
client.verify = False  # Ignore SSL certificate

# Update the local_path to your desired location
client.download_sync(remote_path="type_I/", local_path="Burst/type_I")

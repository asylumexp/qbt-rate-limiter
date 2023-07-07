import requests
import xml.etree.ElementTree as ET
from qbittorrentapi import Client
import logging
from time import sleep
from dotenv import load_dotenv
from os import environ
load_dotenv()

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler and set its level to DEBUG
file_handler = logging.FileHandler('log.log')
file_handler.setLevel(logging.DEBUG)

# Create a console handler and set its level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

while True:
    # API endpoint to get current sessions
    endpoint = f'http://localhost:32400/status/sessions?X-Plex-Token={environ["PLEX_TOKEN"]}'

    # Send a GET request to the API endpoint
    response = requests.get(endpoint)

    client = Client(host=environ["QBT_HOST"],
                    username=environ["QBT_USER"],
                    password=environ["QBT_PASS"])

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        size = root.attrib.get('size', '0')
        if size != "0":
            logger.info("Someone is streaming from Plex!")
            sessions = root.findall('./Video')
            for session in sessions:
                user = session.find('./User').attrib['title']
                title = session.attrib['title']
                logger.info(f"User: {user}, Title: {title}")

            try:
                client.transfer_set_upload_limit("200000")
            except:
                logger.info("Failed to set upload speed limit in qBittorrent.")
            finally:
                logger.info("Upload speed limit set in qBittorrent.")
        else:
            logger.info("No one is currently streaming from Plex.")
            try:
                client.transfer_set_upload_limit("")
            except:
                logger.info("Could not remove upload limit in qBittorrent.")
            finally:
                logger.info("Removed upload speed limit in qBittorrent.")
    else:
        logger.info("Failed to retrieve sessions from Plex API.")

    sleep(30)

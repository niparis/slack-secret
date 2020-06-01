import logging
import os
import urllib
import json
from typing import List, Dict, Any
import time

from slack.errors import SlackApiError
from tqdm import tqdm

from .lib import OUTPUT_FOLDER, download_images

logger = logging.getLogger(__name__)


def _get_channels_dict(client) -> Dict[str, str]:
    resp = client.conversations_list(types="private_channel")
    return {channel['id']: channel['name'] for channel in resp.data['channels']}


def list_private_channels(client):
    channels = _get_channels_dict(client)

    for channel_id, channel_name in channels.items():
        print(f"{channel_name} - ID: [{channel_id}]")

    ts = str(time.time())
    save_path = os.path.join(OUTPUT_FOLDER, f'private-channels-{ts}.json')
    with open(save_path, 'w') as fout:
        fout.write(json.dumps(channels))

    print(f'*****' * 4)    
    print(f'Saved to {save_path}')
    print(f'*****' * 4)

def _get_all_channel_data(client, channel_id: str) -> List[dict]:
    full_data = []

    try:
        response = client.conversations_history(channel=channel_id)
    except SlackApiError:
        print('Unknown channel id')

    full_data.extend(response.data['messages'])
    while True:
        cursor = response.get('response_metadata', {}).get('next_cursor')
        # print(f"date is {response.data['messages'][0]['ts']}")
        if cursor:
            response = client.conversations_history(channel=channel_id, cursor=cursor)
        else:
            break
            
        full_data.extend(response.data['messages'])

    return full_data

def save_private_channel(client, channel_id: str):
    my_channels = _get_channels_dict(client)
    channel_name = my_channels[channel_id]

    full_data = _get_all_channel_data(client, channel_id=channel_id)
    print(f"{len(full_data)} Messages downloaded, now let's download the images")
    main_folder = os.path.join(OUTPUT_FOLDER, f'{channel_id} - {channel_name}')
    images_folder = os.path.join(main_folder, 'images')    
    os.makedirs(images_folder, exist_ok=True)

    download_images(full_data, client.token, images_folder)

    with open(os.path.join(main_folder, f'messages-{channel_id}.json'), 'w') as fout:
        fout.write(json.dumps(full_data))
        

def save_all_private_channels(client):
    for channel_id, channel_name in _get_channels_dict(client).items():
        print(f"Downloading {channel_name}")
        save_private_channel(client, channel_id)
        print("*****" * 5)

    print("All private channels downloaded")


def delete_private_channel(client, channel_id: str):
    full_data = _get_all_channel_data(client, channel_id=channel_id)
    print("Messages downloaded, now let's DELETE all messages")
    confirmation = input("Please type YES to proceed: ")
    if confirmation != 'YES':
        import sys
        print('Not deleting.')
        sys.exit()

    for message in tqdm(full_data):
        # deleting all the threaded messages if needed
        if 'thread_ts' in message:
            resp = client.conversations_replies(channel=channel_id, ts=message['ts'])
            for thread_message in resp.data['messages'][1:]:
                client.chat_delete(channel=channel_id, ts=thread_message['ts'])

        client.chat_delete(channel=channel_id, ts=message['ts'])

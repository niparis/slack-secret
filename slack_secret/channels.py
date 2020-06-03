import json
import logging
import os
import time

from typing import Dict

from .lib import OUTPUT_FOLDER
from .lib import delete_generic_channel
from .lib import save_generic_channel


logger = logging.getLogger(__name__)


def _get_channels_dict(client) -> Dict[str, str]:
    resp = client.conversations_list(types="private_channel")
    return {channel["id"]: channel["name"] for channel in resp.data["channels"]}


def list_private_channels(client):
    channels = _get_channels_dict(client)

    for channel_id, channel_name in channels.items():
        print(f"{channel_name} - ID: [{channel_id}]")

    ts = str(time.time())
    save_path = os.path.join(OUTPUT_FOLDER, f"private-channels-{ts}.json")
    with open(save_path, "w") as fout:
        fout.write(json.dumps(channels))

    print(f"*****" * 4)
    print(f"Saved to {save_path}")
    print(f"*****" * 4)


def save_private_channel(client, channel_id: str):
    my_channels = _get_channels_dict(client)
    channel_name = my_channels[channel_id]

    save_generic_channel(client, channel_id, channel_name)


def save_all_private_channels(client):
    for channel_id, channel_name in _get_channels_dict(client).items():
        print(f"Downloading {channel_name}")
        save_private_channel(client, channel_id)
        print("*****" * 5)

    print("All private channels downloaded")


def delete_private_channel(client, channel_id: str):
    delete_generic_channel(client, channel_id)

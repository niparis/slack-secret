from typing import Optional

from .lib import delete_generic_channel
from .lib import save_generic_channel
from .users import _get_user_dict


def list_all_im(client):
    resp = client.conversations_list(types="im")
    users = _get_user_dict(client)
    for im in resp.data["channels"]:
        print(f"channel_id: {im['id']} - name: {users[im['user']]['name']}")


def _get_channelid_from_name(client, name) -> Optional[str]:
    users = _get_user_dict(client)
    resp = client.conversations_list(types="im")
    for conversation in resp.data["channels"]:
        if users[conversation["user"]]["name"] == name:
            return conversation["id"]


def save_single_im(client, name):
    channel_id = _get_channelid_from_name(client, name)
    if channel_id:
        save_generic_channel(client, channel_id=channel_id, channel_name=name)
    else:
        print(f"Could not find {name}")


def save_all_im(client):
    resp = client.conversations_list(types="im")
    for userid, user_obj in resp.keys():
        save_single_im(client, user_obj["name"])


def delete_single_im(client, name):
    channel_id = _get_channelid_from_name(client, name)
    if channel_id:
        delete_generic_channel(client, channel_id)
    else:
        print(f"Could not find {name}")

import datetime as dt
import json
import os
import socket
import time
import urllib.request

from typing import Any
from typing import List

from slack.errors import SlackApiError
from tqdm import tqdm

from .main import OUTPUT_FOLDER


def _download_safe(opener, url: str, localpath: str):
    urllib.request.install_opener(opener)
    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            retries += 1
            urllib.request.urlretrieve(url, localpath)

        except urllib.error.HTTPError as ex:
            print(f"could not download {url}")
            print(str(ex))
            break

        except socket.timeout:
            print(f"timeout on {url}")
            time.sleep(retries ** 2)


def download_file(string: str, token: str, images_folder: str) -> str:
    socket.setdefaulttimeout(5)

    if type(string) is not str:
        return string

    if not (string.lower().endswith((".png", ".jpg", ".jpeg")) and string.lower().startswith("http")):
        return string

    fname = "-".join(string.split("/")[2:])
    domain = string.split("/")[2]
    localpath = os.path.join(images_folder, fname)
    if domain in ("files.slack.com", "a.slack-edge.com"):
        opener = urllib.request.build_opener()
        opener.addheaders = [("Authorization", f"Bearer {token}")]
        _download_safe(opener=opener, url=string, localpath=localpath)

    elif domain in ("avatars.slack-edge.com",):
        opener = urllib.request.build_opener()
        urllib.request.install_opener(opener)
        _download_safe(opener=opener, url=string, localpath=localpath)

    socket.setdefaulttimeout(30)
    return fname


def download_images_in_message(value, token: str, images_folder: str) -> Any:

    if "files" in value:
        new_files = []
        for file in value["files"]:
            new_dict = {k: download_file(v, token, images_folder) for k, v in file.items()}
            new_files.append(new_dict)

        value["files"] = new_files

    return value


def download_all_messages(messages: list, client, images_folder: str):
    messages_new = []
    for message in tqdm(messages):
        new_message = download_images_in_message(value=message, token=client.token, images_folder=images_folder)
        messages_new.append(new_message)

    return messages_new


def download_images(value: Any, token: str, images_folder: str) -> Any:

    if type(value) is str:
        return download_file(value, token, images_folder)
    elif type(value) is dict:
        for k, v in value.items():
            try:
                localpath = download_images(v, token, images_folder)
            except IndexError:
                print(k, v)
                raise
            if localpath:
                value[k] = localpath
        return value
    elif type(value) in (list, tuple):
        return [download_images(elem, token, images_folder) for elem in value]
    else:
        return value


def _get_all_channel_data(client, channel_id: str) -> List[dict]:
    """ Gets all the conversation history of a channel_id in a single list
    """
    full_data = []

    try:
        response = client.conversations_history(channel=channel_id)
    except SlackApiError:
        print("Unknown channel id")

    full_data.extend(response.data["messages"])
    while True:
        cursor = response.get("response_metadata", {}).get("next_cursor")
        date_str = dt.datetime.utcfromtimestamp(int(response.data["messages"][0]["ts"].split(".")[0]))
        print(f"date is {date_str}")
        if cursor:
            response = client.conversations_history(channel=channel_id, cursor=cursor)
        else:
            break

        full_data.extend(response.data["messages"])

    return full_data


def _get_all_channel_data_gen(client, channel_id: str) -> List[dict]:
    """ Gets all the conversation history of a channel_id in a single list
    """

    try:
        response = client.conversations_history(channel=channel_id)
    except SlackApiError:
        print("Unknown channel id")

    date_str = dt.datetime.utcfromtimestamp(int(response.data["messages"][0]["ts"].split(".")[0]))
    print(f"date is {date_str}")
    yield response.data["messages"]

    while True:
        cursor = response.get("response_metadata", {}).get("next_cursor")
        date_str = dt.datetime.utcfromtimestamp(int(response.data["messages"][0]["ts"].split(".")[0]))
        print(f"date is {date_str}")
        if cursor:
            response = client.conversations_history(channel=channel_id, cursor=cursor)
        else:
            break

        yield response.data["messages"]


def save_generic_channel(client, channel_id: str, channel_name: str) -> None:
    """ Saves all the messages and images from the supplied channel_id in a folder.
    The channel_name is used to create the name of the folder.
    """
    full_data = _get_all_channel_data(client, channel_id=channel_id)
    print(f"{len(full_data)} Messages downloaded, now let's download the images")
    main_folder = os.path.join(OUTPUT_FOLDER, f"{channel_id} - {channel_name}")
    images_folder = os.path.join(main_folder, "images")
    os.makedirs(images_folder, exist_ok=True)
    download_all_messages(full_data, client=client, images_folder=images_folder)

    with open(os.path.join(main_folder, f"messages-{channel_id}.json"), "w") as fout:
        fout.write(json.dumps(full_data))


def _delete_message_with_exclusion(*, client, channel_id: str, message: str, exclusion_list: list, ts: str) -> None:
    user = message.get("user")
    if not user or user not in exclusion_list:
        try:
            client.chat_delete(channel=channel_id, ts=ts)
        except SlackApiError as ex:
            if ex.response.data["error"] == "cant_delete_message":
                if user and "thread_ts" not in message:
                    exclusion_list.append(user)
                else:
                    pass
            elif ex.response.data["error"] in ("message_not_found", "thread_not_found"):
                pass
            else:
                raise ex


def delete_generic_channel(client, channel_id: str) -> None:
    """ Deletes all the messages that the client is allowed to delete in the supplied channel_id
    """
    print(f"Are you sure you want to DELETE all messages with {channel_id}")
    confirmation = input("Please type YES to proceed: ")
    if confirmation != "YES":
        import sys

        print("Not deleting.")
        sys.exit()

    exclusion_list = []
    for page in _get_all_channel_data_gen(client, channel_id=channel_id):
        for message in tqdm(page):
            # deleting all the threaded messages if needed
            if "thread_ts" in message:
                resp = client.conversations_replies(channel=channel_id, ts=message["ts"])
                for thread_message in resp.data["messages"][1:]:
                    _delete_message_with_exclusion(
                        client=client,
                        channel_id=channel_id,
                        message=message,
                        exclusion_list=exclusion_list,
                        ts=thread_message["ts"],
                    )

            _delete_message_with_exclusion(
                client=client, channel_id=channel_id, message=message, exclusion_list=exclusion_list, ts=message["ts"]
            )

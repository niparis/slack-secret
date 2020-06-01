import json
import os

from tqdm import tqdm

from slack_secret.main import OUTPUT_FOLDER
from slack_secret.lib import download_images


def _get_user_dict(client) -> Dict[str, dict]:
    response = client.users_list()
    users = response["members"]
    return {elem['id']: elem for elem in users}


def save_users(client):
    user_dict = _get_user_dict(client)
    folder = os.path.join(OUTPUT_FOLDER, 'users')
    images_folder = os.path.join(folder, 'images')
    os.makedirs(images_folder, exist_ok=True)

    for userid, user in tqdm(user_dict.items()):
        user = download_images(user, images_folder=images_folder, token=client.token)

    with open(os.path.join(folder, 'users.json'), 'w') as fout:
        fout.write(json.dumps(user_dict))
        
    
import urllib.request 
import os
from typing import Any

from slack_secret.main import OUTPUT_FOLDER


def download_file(string: str, token: str, images_folder: str) -> str:

    if not (string.lower().endswith(('.png', '.jpg', '.jpeg')) and  string.lower().startswith('http')):
        return string
    
    fname = '-'.join(string.split('/')[2:])
    domain = string.split('/')[2]            
    localpath = os.path.join(images_folder, fname)         
    if domain in ('files.slack.com', 'a.slack-edge.com' ):             
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', f'Bearer {token}')]
        urllib.request.install_opener(opener)
        try:
            urllib.request.urlretrieve(string, localpath)
        except urllib.error.HTTPError as ex:
            print(f'could not download {string} from {domain}')
            print(str(ex))  

    elif domain in ('avatars.slack-edge.com', ):
        opener = urllib.request.build_opener()
        urllib.request.install_opener(opener)
        try:
            resp = urllib.request.urlretrieve(string, localpath)        
        except urllib.error.HTTPError as ex:
            print(f'could not download {string} from {domain}')
            print(str(ex))

        else:
            localpath = 'protected-file'

    return localpath

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
                        

        
    
            
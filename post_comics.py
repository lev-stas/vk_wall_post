import requests
import os
import random
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

def get_comics(dir_name):
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    comics_data = response.json()
    last_comics = comics_data['num']
    random_number = random.randint(1, last_comics)
    comics_response = requests.get(f'https://xkcd.com/{random_number}/info.0.json')
    comics_response.raise_for_status()
    comics = comics_response.json()
    image_link = comics['img']
    file_name = image_link.split('/')[-1]
    photo_path = os.path.join(dir_name, file_name)
    comics_picture = requests.get(image_link)
    comics_picture.raise_for_status()
    with open (photo_path, 'wb') as file:
        file.write(comics_picture.content)
    return comics['alt']


def get_wall_upload_server(group_id, token, api_ver):
    params = {
        'group_id': group_id,
        'access_token': token,
        'v': api_ver
    }
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise requests.exceptions.HTTPError(result['error'])
    upload_url = result['response']['upload_url']
    return upload_url


def make_upload_img_request(upload_server_url, file):
    response = requests.post(upload_server_url, files={'photo': file})
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise requests.exceptions.HTTPError(result['error'])
    upload_result = {
        'server': result['server'],
        'photo': result['photo'],
        'hash': result['hash']
    }
    return upload_result


def make_save_img_request(params):
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise requests.exceptions.HTTPError(result['error'])
    photo_attributes = result['response'][0]
    
    save_result = {
        'owner_id': photo_attributes['owner_id'],
        'media_id': photo_attributes['id']
    }
    return save_result

def make_post_img_request(group_id, token, api_ver, owner_id, media_id, message):
    params = {
        'owner_id': - int(group_id),
        'access_token': token,
        'v': api_ver,
        'attachments': f'photo{owner_id}_{media_id}',
        'message':  message,
        'from_group': 1
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()
    result = response.json()
    if 'error' in result:
        raise requests.exceptions.HTTPError(result['error'])


def post_comics(token, group_id, api_ver, images_dir, logger):
    try:
        comics_message = get_comics(images_dir)
        upload_server_url = get_wall_upload_server(group_id, token, api_ver)
        images = os.listdir(images_dir)
        for image in images:
            photo_path = os.path.join(images_dir, image)
            if not os.path.isfile(photo_path):
                continue
            with open(photo_path, 'rb') as file:
                upload_attributes = make_upload_img_request(upload_server_url, file)
                save_request_params = {
                    'group_id': group_id,
                    'access_token': token,
                    'v': api_ver,
                    'server': upload_attributes['server'],
                    'photo': upload_attributes['photo'],
                    'hash': upload_attributes['hash']
                }
                photo_upload_ids = make_save_img_request(save_request_params)
                photo_owner_id = photo_upload_ids['owner_id']
                photo_media_id = photo_upload_ids['media_id']
                make_post_img_request(group_id, token, api_ver, photo_owner_id, photo_media_id, comics_message)   
    except requests.exceptions.HTTPError as err:
        logger.error(err)
    finally:
        for file in os.listdir(images_dir):
            file_path = os.path.join(images_dir, file)
            if not os.path.isfile(file_path):
                continue
            os.remove(file_path)


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_ACCOUNT_ACCESS_TOKEN')
    vk_group_id = int(os.getenv('VK_GROUP_ID'))

    vk_api_url = 'https://api.vk.com/method/'
    vk_api_version = '5.103'
    images_dir = 'images'
    logs_dir = 'logs'
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    logs_path = os.path.join(logs_dir, 'vk_comics_log.log')

    vk_logger = logging.getLogger('vk_comics_post_logger')
    logs_handler = RotatingFileHandler(logs_path, maxBytes=1024, backupCount=5)
    vk_logger.addHandler(logs_handler)

    post_comics(vk_token, vk_group_id, vk_api_version, images_dir, vk_logger)
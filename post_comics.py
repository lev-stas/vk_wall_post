import requests
import os
from dotenv import load_dotenv
import random


def get_comics(dir_name):
    response = requests.get('https://xkcd.com/info.0.json')
    comics_data = response.json()
    last_comics = comics_data['num']
    comics_number = random.randint(1, last_comics)
    random_response = requests.get(f'https://xkcd.com/{comics_number}/info.0.json')
    comics = random_response.json()
    image_link = comics['img']
    extension = comics['img'].split('.')[-1]
    file_name = comics['title']
    comics_picture = requests.get(image_link)
    with open (f'{dir_name}/{file_name}.{extension}', 'wb') as file:
        file.write(comics_picture.content)
    return comics['alt']


def get_upload_photo(group_id, token, api_url, api_version, dir_name,  message):
    url_params = {
        'group_id': group_id,
        'access_token': token,
        'v': api_version
    }
    url_response = requests.get(f'{api_url}photos.getWallUploadServer', params = url_params)
    url_response.raise_for_status()
    url_answer = url_response.json()
    upload_url = url_answer['response']['upload_url']
    images = os.listdir(dir_name)
    for image in images:
        photo_path = f'{dir_name}/{image}'
        if not os.path.isfile(photo_path):
            continue
        with open (photo_path, 'rb') as file:
            upload_response = requests.post(upload_url, files={'photo':file})
            upload_response.raise_for_status()
            upload_result = upload_response.json()
            save_params = {
                'group_id': group_id,
                'access_token': token,
                'v': api_version,
                'server': upload_result['server'],
                'photo': upload_result['photo'],
                'hash': upload_result['hash']
            }
            save_request = requests.post(f'{api_url}photos.saveWallPhoto', params = save_params)
            save_result = save_request.json()
            photo_owner_id = save_result['response'][0]['owner_id']
            photo_media_id = save_result['response'][0]['id']
            
            post_params = {
                'owner_id': -group_id,
                'access_token': token,
                'v': api_version,
                'attachments': f"photo{photo_owner_id}_{photo_media_id}",
                'message': message,
                'from_group': 1
                
            }
            post_request = requests.post(f'{api_url}wall.post', params=post_params)
        os.remove(photo_path)


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_ACCOUNT_ACCESS_TOKEN')
    vk_group_id = int(os.getenv('VK_GROUP_ID'))

    vk_api_url = 'https://api.vk.com/method/'
    vk_api_version = '5.103'
    images_dir = 'images'
    os.makedirs(images_dir, exist_ok=True)

    comics_message = get_comics(images_dir)
    get_upload_photo(vk_group_id, vk_token, vk_api_url, vk_api_version, images_dir, comics_message)

#! /usr/bin/python3
#  -*- coding: UTF-8 -*-

# pip install request
# pip install vk_api
# pip install BeautifulSoup4

import datetime
import os
import os.path

import requests
import vk_api
from vk_api import audio

from tqdm import tqdm

vk_file = 'vk_config.v2.json'


path = os.path.expanduser(r'~\Downloads') + r'\music_vk'
print('Путь загрузки:', path)

if not os.path.exists(path):
    os.makedirs(path)


# Авторизация
def auth():
    vk_login = input('Введите телефон или email: ')
    vk_password = input('Введите пароль: ')
    vk_id = input('Введите id: ')
    return vk_login, vk_password, vk_id


# Если включена функция подтверждения входа
def two_step_auth():
    code = input('Введите код подтверждения входа: ')
    remember_device = False
    return code, remember_device


def main():
    vk_login, vk_password, vk_id = auth()
    vk_session = vk_api.VkApi(login=vk_login, password=vk_password, auth_handler=two_step_auth)
    try:
        vk_session.auth()
        print('Авторизация')
        vk_session.get_api()
        vk_audio = audio.VkAudio(vk_session)
        os.chdir(path)

        i = vk_audio.get(owner_id=vk_id)[0]
        r = requests.get(i['url'])

        if r.status_code == 200:
            print('Успех')
            try:
                song = 0
                time_start = datetime.datetime.now()
                print('Начало загрузки', datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y'))
                for i in vk_audio.get(owner_id=vk_id):
                    try:
                        song += 1
                        r = requests.get(i['url'], stream=True)
                        size = int(r.headers['content-length'])
                        if r.status_code == 200:
                            with open(str(song) + '_' + i['artist'] + ' - ' + i['title'] + '.mp3', 'wb') as output_file:
                                print('Загрузка:', i['artist'] + ' - ' + i['title'])
                                for data in tqdm(iterable=r.iter_content(chunk_size=1024), total=size / 1024,
                                                 unit='KB'):
                                    output_file.write(data)
                    except OSError:
                        print('Ошибка загрузки:', song, i['artist'] + ' - ' + i['title'])
                time_end = datetime.datetime.now()
                print('Загружено', len(next(os.walk(path))[2]), 'песен за', (time_end - time_start))
                input('Нажмите ENTER для выхода')
            except vk_api.AuthError as error_msg:
                print(error_msg)
                input('Нажмите ENTER для выхода')
                return
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return


if __name__ == '__main__':
    main()
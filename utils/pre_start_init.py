# -*- coding: utf-8 -*-
import logging

import re
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI


# Создаём словарь категорий из словаря в файле
def cat_dictionary() -> dict:
    dict_cat = str()
    file = 'Classifier/content/Test_res_cat_3.0.csv'
    new_file = 'Classifier/content/Test_res_cat_4.0.json'

    # with open(file, encoding="UTF-8") as dict_to_pars:
    #     for line in dict_to_pars:
    #         line = line.strip('\n')
    #         dict_cat += line
    #     dict_cat = le(dict_cat)

    with open(new_file) as json_file:
        new_data = json.load(json_file)

    for key, value in new_data.items():
        for i in range(len(value['data'])):
            for lma, count in value['data'][i].items():
                if re.search(r'\d{1,9}', lma) or len(lma) < 2 or lma in ['интересовать', 'сообщать']:
                    value['data'][i][lma] = 0
                    # print('Что-то нашли и заменили')
    dict_cat = new_data
    return dict_cat

dict_category = cat_dictionary()

auth_token = os.environ.get("AUTH_TOKEN")
logging.debug(auth_token)

BASE_DIR = Path(__file__).resolve().parent.parent
paths = {
    "BASE_DIR": BASE_DIR,
    "model_dir": BASE_DIR / 'models' / 'vosk-vosk_model-small-ru-0.22',
    "test_file": BASE_DIR / 'content' / 'g_audio.mp3',
    # file_path = BASE_DIR/'content'/'2723.mp3'
    "trash_folder": BASE_DIR / 'trash',
    "model_dir_small": BASE_DIR / 'models' / 'vosk-model-small-ru-0.22',
    "model_dir_complete": BASE_DIR / 'models' / 'vosk-model-ru-0.42',
    # "model_dir_complete": Path('D:\\coding\\vosk-model-ru-0.42'),
}

if os.environ.get("PROD") == "True":
    is_prom = True
else:
    is_prom = False


# class StateAudioClassifier:
#     def __init__(self):
#         self.request_limit = buffer_size
#         self.request_data = dict()
#
#
# State = StateAudioClassifier()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_start
    logging.debug("Приложение запущено")
    # await state_audio_classifier.infinity_worker()
    yield  # on_stop
    logging.debug("Приложение завершено")


app = FastAPI(lifespan=lifespan,
              version="0.1",
              docs_url='/docs',
              root_path='/Classifier',
              title='Сервис классификации обращений клиентов ООО "НЮС"'
              )

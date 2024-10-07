# -*- coding: utf-8 -*-
from utils.logging import logger

import re
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

auth_token = os.environ.get("AUTH_TOKEN")
logger.debug(auth_token)

BASE_DIR = Path(__file__).resolve().parent.parent
paths = {
    "BASE_DIR": BASE_DIR,
    "model_full_gpu": BASE_DIR / 'models' / 'batch_vosk-model-ru-0.42',
    "test_file": BASE_DIR /'trash'/'2724.1726990043.1324706.wav',
    "trash_folder": BASE_DIR / 'trash',
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on_start
    logger.debug("Приложение запущено")
    # await state_audio_classifier.infinity_worker()
    yield  # on_stop
    logger.debug("Приложение завершено")

app = FastAPI(lifespan=lifespan,
              version="0.1",
              docs_url='/docs',
#               root_path='/root',
              title='ASR-Vosk-GPU on BatchModel'
              )

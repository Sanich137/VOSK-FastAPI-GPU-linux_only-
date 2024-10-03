# -*- coding: utf-8 -*-
import os
import logging
from vosk import SetLogLevel
import datetime

logging.basicConfig(
    # level=logging.INFO,
    # filename=f'Services-from-{datetime.datetime.now().date()}.log',
    # filemode='a',
    level=os.getenv('LOGGING_LEVEL', 'INFO'),
    # level=logging.DEBUG,  # Можно заменить на другой уровень логирования.
    format=os.getenv('LOGGING_FORMAT',  u'#%(levelname)-8s %(filename)s [LINE:%(lineno)d] [%(asctime)s]  %(message)s',
                     )
                    )

logger = logging.getLogger(__name__)

if os.getenv('LOGGING_LEVEL') == "DEBUG":
    SetLogLevel(0)
else:
    logging.info("Vosk logging only error mode enabled")
    SetLogLevel(-1)

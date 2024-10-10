from dbm import error

import ujson
import asyncio
from utils.pre_start_init import app, WebSocket, WebSocketException

from utils.logging import logger
from models.vosk_model import model
from vosk import BatchRecognizer
from models.fast_api_models import WebSocketModel

@app.post("/ws")
async def get_not_websocket(ws:WebSocketModel):
    """Описание для вебсокета ниже в описании WebSocketModel """
    return f"Прочти инструкцию в Schemas - 'WebSocketModel'"

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    sample_rate=8000
    online_recognizer = BatchRecognizer(model, sample_rate)
    wait_null_answers=True
    await ws.accept()

    while True:
        try:
            message = await ws.receive()
        except Exception as wse:
            logger.error(f"receive WebSocketException - {wse}")
            return

        # Load configuration if provided
        if isinstance(message, dict) and message.get('text'):
            try:
                if message.get('text') and 'config' in message.get('text'):
                    jobj = ujson.loads(message.get('text'))['config']
                    sample_rate = jobj.get('sample_rate', 8000)
                    wait_null_answers = jobj.get('wait_null_answers', wait_null_answers)
                    online_recognizer = BatchRecognizer(model, sample_rate)
                    logger.debug(f"Task received, config -  {jobj}")
                    logger.info(f"Task received, config -  {jobj}")
                    continue
                elif message.get('text') and 'eof' in message.get('text'):
                    logger.debug("EOF received")
                    logger.info("EOF received")
                    break
                else:
                    logger.debug("Can`t recognise text message")
                    logger.info("Can`t recognise text message")

            except Exception as e:
                logger.error(f'Error text message compiling. Message:{message} - error:{e}')

        elif isinstance(message, dict) and message.get('bytes'):
            try:
                online_recognizer.AcceptWaveform(message.get('bytes'))
            except Exception as e:
                logger.error(f"AcceptWaveform error - {e}")
            else:
                while online_recognizer.GetPendingChunks() > 0:
                    await asyncio.sleep(0.1)
                else:
                    try:
                        result = online_recognizer.Result()
                    except Exception as e:
                        logger.error(f"online_recognizer.Result() error - {e}")
                    else:
                        try:
                            if len(result) > 0:
                                result = ujson.decode(result)
                        except Exception as e:
                            logger.error(f"result to str decoding error {e}")
                            send_message = {"silence": True,
                                            "data": None,
                                            "error": f"result to str decoding error {e}"
                                            }
                            logger.debug(send_message)
                            try:
                                await ws.send_json(send_message)
                            except Exception as e:
                                logger.error(f"Send_json exception - {e}, work canceled")
                                return
                        else:
                            if len(result) == 0:
                                if wait_null_answers:
                                    send_message = {"silence" : True,
                                                    "data": None,
                                                    "error": None
                                                    }
                                    logger.debug(send_message)
                                    try:
                                        await ws.send_json(send_message)
                                    except Exception as e:
                                        logger.error(f"Send_json exception - {e}, work canceled")
                                        return
                                else:
                                    logger.debug("sending silence partials skipped")
                                    continue
                            else:
                                send_message = {"silence": False,
                                                "data": result,
                                                "error": None
                                                }
                                logger.info(send_message)
                                logger.debug(send_message)

                                try:
                                    await ws.send_json(send_message)

                                except Exception as e:
                                    logger.error(f"Send_json exception - {e}, work canceled")
                                    return

        else:
            logger.error(message)
            send_message = {"silence": False,
                            "data": None,
                            "error": "Похоже text не строка. Сообщи, проверим"
                            }
            try:
                await ws.send_json(send_message)
            except Exception as e:
                logger.error(f"Send_json exception - {e}, work canceled")

    while online_recognizer.GetPendingChunks() > 0:
        await asyncio.sleep(0.1)

    result = online_recognizer.Result()

    if len(result) > 0:
        result = ujson.decode(result)

    logger.debug(result)
    logger.info(result)
    send_message = {"silence": False,
                    "data": result,
                    "error": None
                    }
    try:
        await ws.send_json(send_message)
    except Exception as e:
        logger.error(f"send_json exception - {e}")
        return

    await ws.close()
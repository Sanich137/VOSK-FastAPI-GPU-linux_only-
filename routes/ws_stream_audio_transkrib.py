from dbm import error

import ujson
import asyncio

from pydub.effects import strip_silence

from utils.pre_start_init import app, WebSocket, WebSocketException

from utils.logging import logger
from models.vosk_model import model
from vosk import BatchRecognizer
from models.fast_api_models import WebSocketModel



async def send_messages(_socket, _data=None, _silence=True, _error=None, log_comment=None, _last_message=False):
    ws = _socket
    is_ok = False
    snd_mssg = {"silence": _silence,
                    "data": _data,
                    "error": _error,
                    "last_message": _last_message
                    }
    try:
        await ws.send_json(snd_mssg)
    except Exception as e:
        logger.error(f"send_message on '{log_comment}', exception - {e}")
    else:
        logger.debug(snd_mssg)
        logger.info(snd_mssg)
        is_ok = True

    return is_ok


@app.post("/ws")
async def post_not_websocket(ws:WebSocketModel):
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

        logger.debug(f'Raw message - {message}')

        if isinstance(message, dict) and message.get('text'):
            try:
                if message.get('text') and 'config' in message.get('text'):
                    json_cfg = ujson.loads(message.get('text'))['config']
                    sample_rate = json_cfg.get('sample_rate', 8000)
                    wait_null_answers = json_cfg.get('wait_null_answers', wait_null_answers)
                    online_recognizer = BatchRecognizer(model, sample_rate)
                    logger.info(f"\n Task received, config -  {message.get('text') }")
                    continue
                elif message.get('text') and 'eof' in message.get('text'):
                    logger.debug("EOF received\n")
                    online_recognizer.FinishStream()
                    break
                else:
                    logger.error(f"Can`t recognise  text part of  message {message.get('text')}")

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
                        if len(result) == 0:
                            if wait_null_answers:
                                if not await send_messages(ws, _silence = True, _data = None, _error = None):
                                    logger.error(f"send_message not ok work canceled")
                                    return
                            else:
                                logger.debug("sending silence partials skipped")
                                continue
                        elif 'text' in result and len(ujson.decode(result).get('text')) == 0:
                            logger.debug("No text in result. Skipped")
                            continue

                        else:
                            try:
                                result = ujson.decode(result)
                            except Exception as e:
                                logger.error(f"result to dict decoding error {e}")
                            else:
                                if not await send_messages(ws, _silence=False, _data=result, _error=None):
                                    logger.error(f"send_message not ok work canceled")
                                    return
        else:

            error = f"Can`t parse message - {message}"
            logger.error(error)

            if not await send_messages(ws, _silence=False, _data=None, _error=error):
                logger.error(f"send_message not ok work canceled")
                return


    while online_recognizer.GetPendingChunks() > 0:
        await asyncio.sleep(0.1)
    else:
        try:
            result = online_recognizer.Result()
        except Exception as e:
            logger.error(f"online_recognizer.Result() error - {e}")
        else:
            if len(result) == 0:
                if wait_null_answers:
                    if not await send_messages(ws, _silence=True, _data=None, _error=None):
                        logger.error(f"send_message not ok work canceled")
                        return
                else:
                    logger.debug("sending silence partials skipped")
            elif 'text' in result and len(ujson.decode(result).get('text')) == 0:
                logger.debug("No text in result. Skipped")
            else:
                try:
                    result = ujson.decode(result)
                except Exception as e:
                    logger.error(f"result to dict decoding error {e}")
                else:
                    if not await send_messages(ws, _silence=False, _data=result, _error=None, _last_message=True):
                        logger.error(f"send_message not ok work canceled")
                        return

    await ws.close()
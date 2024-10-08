import ujson
import asyncio
from utils.pre_start_init import app, WebSocket, WebSocketDisconnect
from utils.logging import logger
from models.vosk_model import model
from vosk import BatchRecognizer, BatchModel, GpuInit
from models.fast_api_models import WebSocketModel

@app.post("/ws")
async def get_not_websocket(ws:WebSocketModel):
    """Описание для вебсокета ниже в описании WebSocketModel """
    return f"Прочти инструкцию в Schemas - 'WebSocketModel'"

@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    sample_rate=8000
    online_recognizer = BatchRecognizer(model, sample_rate)
    result = None
    wait_null_answers=True
    await websocket.accept()

    while True:
        message = await websocket.receive()
        # Load configuration if provided
        if isinstance(message, dict) and message.get('text'):
            try:
                if message.get('text') and 'config' in message.get('text'):
                    jobj = ujson.loads(message.get('text'))['config']
                    logger.info(f"Config - {jobj}", )
                    sample_rate = jobj.get('sample_rate', 8000)
                    wait_null_answers = jobj.get('wait_null_answers', wait_null_answers)
                    online_recognizer = BatchRecognizer(model, sample_rate)
                    continue
                elif message.get('text') and 'eof' in message.get('text'):
                    break

            except Exception as e:
                logger.error(f'{message} - {e}')

        elif isinstance(message, dict) and message.get('bytes'):
            try:
                online_recognizer.AcceptWaveform(message.get('bytes'))
                while online_recognizer.GetPendingChunks() > 0:
                    await asyncio.sleep(0.1)
                else:
                    result = online_recognizer.Result()

                if len(result) == 0:
                    if wait_null_answers:
                        send_message = {"silence" : True,
                                        "data": None,
                                        "error": None
                                        }
                        await websocket.send_json(send_message)
                    else:
                        logger.debug("sending silence partials skipped")
                        continue
                else:
                    send_message = {"silence": False,
                                    "data": result,
                                    "error": None
                                    }
                    await websocket.send_json(send_message)
                    logger.info(result)
            except Exception as e:
                logger.error(f'Ошибка при обработке сообщения -  {e}')
        else:
            send_message = {"silence": False,
                            "data": None,
                            "error": "Похоже text не строка. Сообщи, проверим"
                            }
            await websocket.send_json(send_message)

    while online_recognizer.GetPendingChunks() > 0:
        await asyncio.sleep(0.1)

    result = online_recognizer.Result()
    send_message = {"silence": False,
                    "data": result,
                    "error": None
                    }
    await websocket.send_json(send_message)
    logger.info(result)

    await websocket.close()
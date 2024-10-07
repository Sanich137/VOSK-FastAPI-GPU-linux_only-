import ujson
import asyncio
from utils.pre_start_init import app, WebSocket, WebSocketDisconnect
from utils.logging import logger
from models.vosk_model import model
from vosk import BatchRecognizer, BatchModel, GpuInit
from models.fast_api_models import WebSocketModel

@app.get("/ws")
async def get_not_websocket(wsm:WebSocketModel):
    """Описание для вебсокета"""
    print(f"{wsm.text}")


@app.websocket("/ws")
async def websocket(websocket: WebSocket, ):
    sample_rate=8000
    online_recognizer = BatchRecognizer(model, sample_rate)
    result = None
    wait_null_answers=True
    await websocket.accept()

    while True:
        message = await websocket.receive()
        # Load configuration if provided
        if isinstance(message, dict) and message.get('text'):
            if message.get('text') and 'config' in message.get('text'):
                jobj = ujson.loads(message.get('text'))['config']
                logger.info(f"Config - {jobj}", )
                sample_rate = jobj.get('sample_rate', 8000)
                wait_null_answers = jobj.get('wait_null_answers', wait_null_answers)
                online_recognizer = BatchRecognizer(model, sample_rate)
                continue
            elif message.get('text') and 'eof' in message.get('text'):
                while online_recognizer.GetPendingChunks() > 0:
                    await asyncio.sleep(0.1)
                online_recognizer.FinishStream()
                break
        elif isinstance(message, dict) and message.get('bytes'):
            online_recognizer.AcceptWaveform(message.get('bytes'))
            while online_recognizer.GetPendingChunks() > 0:
                await asyncio.sleep(0.1)

            result = online_recognizer.Result()
            if len(result) == 0:
                if wait_null_answers:
                    await websocket.send_text('{"partial" : ""}')
                else:
                    await websocket.send_json()
                    continue
            else:
                await websocket.send_text(result)
                logger.info(result)


    result = online_recognizer.Result()
    await websocket.send_text(result)
    await websocket.close()
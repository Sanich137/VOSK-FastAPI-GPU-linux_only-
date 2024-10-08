#!/usr/bin/env python3

import asyncio
from asyncio import timeout

import websockets
import sys
import wave
from utils.pre_start_init import paths
import ujson

async def run_test(uri):
    async with websockets.connect(uri) as websocket:
        wait_null_answers = False
        wf = wave.open(str(paths.get('test_file')), "rb")
        config  = {
            "sample_rate": wf.getframerate(),
            "wait_null_answers": wait_null_answers
                }
        await websocket.send(ujson.dumps({'config':config}, ensure_ascii=True))
        buffer_size = 12800 # 0.8 seconds of audio, don't make it too small otherwise compute will be slow

        while True:
            data = wf.readframes(buffer_size)
            if len(data) == 0:
                break
            else:
                await websocket.send(data)
                # print(await websocket.recv())

        await websocket.send('{"eof" : 1}')
        print (await websocket.recv())
        await asyncio.sleep(120)
asyncio.run(run_test('ws://127.0.0.1:49152/ws'))


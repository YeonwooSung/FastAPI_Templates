import asyncio

from fastapi import FastAPI, Depends
from starlette.websockets import WebSocket
import redis.asyncio as redis

app = FastAPI()

redis_connection_pool = redis.ConnectionPool(
    host='...',
    port=1234,
    password='*****'
)


def redis_connection() -> redis.Redis:
    return redis.Redis(connection_pool=redis_connection_pool)


@app.get("/")
async def root():
    return {"hello": "world"}


@app.websocket("/ws")
async def ws_root(websocket: WebSocket, rdb: redis.Redis = Depends(redis_connection)):
    await websocket.accept()

    async def listen_redis():
        ps = rdb.pubsub()
        await ps.psubscribe("test_channel")
        while True:
            message = await ps.get_message(ignore_subscribe_messages=True, timeout=None)
            if message is None:
                continue
            text_message = message['data'].decode('utf-8')
            if text_message == "stop":
                await websocket.send_text("closing the connection")
                break
            await websocket.send_text(text_message)

    async def listen_ws():
        while True:
            message = await websocket.receive_text()
            await rdb.publish("test_channel", message)  # publishing the message to the redis pubsub channel

    await asyncio.wait([listen_ws(), listen_redis()], return_when=asyncio.FIRST_COMPLETED)
    await websocket.close()

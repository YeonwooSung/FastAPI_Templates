import asyncio

from fastapi import FastAPI, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect
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

        # use try-catch for WebSocketDisconnect event
        try:
            while True:
                message = await ps.get_message(ignore_subscribe_messages=True, timeout=None)
                if message is None:
                    continue
                text_message = message['data'].decode('utf-8')
                if text_message == "stop":
                    await websocket.send_text("closing the connection")
                    break
                await websocket.send_text(text_message)
        except WebSocketDisconnect:
            pass

    async def listen_ws():
        # Use 'async for' instead of 'while True' on Websocket
        # Reference: <https://github.com/Kludex/fastapi-tips?tab=readme-ov-file#3-use-async-for-instead-of-while-true-on-websocket>
        async for message in websocket.iter_text():
            await rdb.publish("test_channel", message)  # publishing the message to the redis pubsub channel

    await asyncio.wait([listen_ws(), listen_redis()], return_when=asyncio.FIRST_COMPLETED)
    await websocket.close()

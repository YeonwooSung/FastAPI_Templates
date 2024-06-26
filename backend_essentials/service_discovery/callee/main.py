from typing import Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from datetime import datetime
import httpx

from bs4 import BeautifulSoup

import urllib.parse

from exceptions import UnicornException
from settings import Settings
from log import init_log
from cors import init_cors
from instrumentator import init_instrumentator
from zoo import init_kazoo
from config import Config


app = FastAPI()


ZK_SCRAP_PATH = "/zk/services/scrap/nodes"

my_settings = Settings()
conf = Config(my_settings.CONFIG_PATH)
init_log(app, conf.section("log")["path"])
init_cors(app)
init_instrumentator(app)
zk = init_kazoo(conf.section("zookeeper")["hosts"], None, None)


client = httpx.AsyncClient()

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status,
        content={"code": exc.code, "message": exc.message},
    )

async def call_api(url: str):
    r = await client.get(url)
    return r.text


def parse_opengraph(body: str):
    soup = BeautifulSoup(body, 'html.parser')

    title = soup.find("meta",  {"property":"og:title"})
    url = soup.find("meta",  {"property":"og:url"})
    og_type = soup.find("meta",  {"property":"og:type"})
    image = soup.find("meta",  {"property":"og:image"})
    description = soup.find("meta",  {"property":"og:description"})
    author = soup.find("meta",  {"property":"og:article:author"})

    resp = {}
    scrap = {}
    scrap["title"] = title["content"] if title else None
    scrap["url"] = url["content"] if url else None
    scrap["type"] = og_type["content"] if og_type else None
    scrap["image"] = image["content"] if image else None
    scrap["description"] = description["content"] if description else None
    scrap["author"] = author["content"] if author else None
    resp["scrap"] = scrap

    return resp


@app.get("/api/v1/scrap/")
async def scrap(url: str):
    try:
        url = urllib.parse.unquote(url)
        body = await call_api(url)
        return parse_opengraph(body)
    except Exception as e:
        raise UnicornException(status=400, code=-20000, message=str(e))

def register_into_service_discovery(endpoint):
    node_path = f"{ZK_SCRAP_PATH}/{endpoint}"
    if zk.exists(node_path):
        zk.delete(node_path)
    zk.create(node_path, ephemeral=True, makepath=True)

@app.on_event("startup")
def startup():
    register_into_service_discovery(my_settings.APP_ENDPOINT)

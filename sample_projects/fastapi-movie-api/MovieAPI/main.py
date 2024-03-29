from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from sqlmodel import SQLModel
import sys

# Add the parent directory to the sys.path list
sys.path.append(".")
sys.path.append("..")

# import custom modules
# from MovieAPI.api import actors, movies, subscriptions, token, users
from MovieAPI.utils import limiter, Logger
from MovieAPI.utils.db import engine
from MovieAPI.middlewares import RequestID, RequestLogger
from MovieAPI.api import actors_router, movies_router, subscriptions_router, token_router, users_router


app = FastAPI(title="Movie API server")
app.state.limitter = limiter  # add rate limitter

# add middlewares
app.add_middleware(
    ProxyHeadersMiddleware, trusted_hosts="*"
)  # add proxy headers to prevent logging IP address of the proxy server instead of the client
app.add_middleware(GZipMiddleware, minimum_size=500)  # add gzip compression

# add custom middlewares
app.add_middleware(RequestLogger)
app.add_middleware(RequestID)


@app.on_event("startup")
def on_startup() -> None:
    Logger().get_logger() # init logger
    SQLModel.metadata.create_all(engine)

@app.on_event("shutdown")
def on_shutdown() -> None:
    pass


# add routers
app.include_router(actors_router)
app.include_router(movies_router)
app.include_router(subscriptions_router)
app.include_router(token_router)
app.include_router(users_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', port=8000, reload=True)

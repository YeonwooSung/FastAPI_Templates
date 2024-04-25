from contextlib import asynccontextmanager

from fastapi import FastAPI

from container import Container
from core.fastapi.error import init_error_handler
from core.fastapi.event.middleware import EventHandlerMiddleware
from core.fastapi.responses import ORJSONResponse
from core.fastapi.routes import add_routes
from sqlalchemy.orm import clear_mappers

from modules.author.usecase.addBookToAuthor import event_handler as book_domain_event_impl
from modules.author.infrastructure.persistence import mapper as author_persistence_mapper
from modules.author.infrastructure.query import mapper as author_query_mapper
from modules.author.usecase import router as author_router
from modules.author.usecase.newAuthor import api as new_author_api

from modules.book.infrastructure.persistence import mapper as book_persistence_mapper
from modules.book.infrastructure.query import mapper as book_query_mapper
from modules.book.usecase import router as book_router
from modules.book.usecase.newBook import api as new_book_api
from modules.book.usecase.addAuthor import api as add_author_api
from modules.book.usecase.deleteBook import api as delete_book_api
from modules.book.usecase.findBookByTitle import api as find_book_api


# Init Container
container = Container()

# Get DB from Container
db = container.db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    #
    # app startup
    #

    await db.connect(echo=True)
    await db.create_database()

    author_persistence_mapper.start_mapper()
    author_query_mapper.start_mapper()

    book_persistence_mapper.start_mapper()
    book_query_mapper.start_mapper()

    yield

    #
    # app shutdown
    #

    clear_mappers()

    await db.disconnect()


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
add_routes([author_router, book_router], app)

# IoC (Inversion of Control)
container.wire(
    modules=[
        new_author_api,
        new_book_api,
        add_author_api,
        delete_book_api,
        find_book_api,
    ]
)

app.container = container

app.add_middleware(EventHandlerMiddleware)
init_error_handler(app, 'neos960518@gmail.com')

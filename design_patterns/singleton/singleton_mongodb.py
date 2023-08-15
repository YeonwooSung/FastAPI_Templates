from fastapi import FastAPI, Depends
from pymongo import MongoClient
from typing import Optional


class Database:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.client = MongoClient("mongodb://localhost:27017/")
            cls.instance.db = cls.instance.client["mydatabase"]
        return cls.instance


def get_db() -> Optional[Database]:
    return Database()


app = FastAPI()

@app.get("/")
def read_root(db: Optional[Database] = Depends(get_db)):
    if db:
        result = db.db.my_collection.find_one()
        return {"message": result}
    else:
        return {"message": "Failed to connect to database."}

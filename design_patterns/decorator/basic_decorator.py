from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

def add_greeting(original_function):
    def new_function():
        return {"greeting": "Welcome to my FastAPI application!"} | original_function()
    return new_function

@app.get("/decorated")
@add_greeting
def read_decorated():
    return {"data": "This is some data."}

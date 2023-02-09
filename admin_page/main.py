from fastapi import FastAPI, Depends

from utils.exceptions import ServerHTTPException

def create_app():
    app = FastAPI()
    #TODO
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

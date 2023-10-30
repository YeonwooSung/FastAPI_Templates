from fastapi import FastAPI
import uvicorn

from routers.products import router as product_router
from extensions.batching import enable_batching

app = FastAPI()
app.include_router(product_router)
enable_batching(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

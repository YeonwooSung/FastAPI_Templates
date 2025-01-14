# Performance Tuning

## Use orjson for faster serialization

When serializing data to JSON, using a faster JSON library can improve performance. orjson is a fast JSON library written in Rust.

First, install orjson:
```bash
pip install orjson
```

Then, use orjson to serialize data:
```python
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

app = FastAPI(default_response_class=ORJSONResponse)
class Item(BaseModel):
    item_id: str
    value: float
@app.get("/items/", response_model=list[Item])
async def read_items():
    # Return data directly without extra validation
    return [{"item_id": "Foo", "value": 42.0}, {"item_id": "Bar", "value": 36.0}]
```

## Use uvloop

Many people believe that simply using Uvicorn gives a significant performance boost, but that’s not always the case.
I/O operations need to be carefully planned and orchestrated with a tool like uvloop.

By just installing uvloop, you can achieve a performance improvement!
If uvloop is installed, Uvicorn will automatically use it.

First, install uvloop:
```bash
pip install uvloop
```

Then, use uvloop with Uvicorn:
```bash
uvicorn main:app --loop uvloop
```

## Use httptools

`httptools` is faster than "H11," which appears to be the default.
`httptools` is a Python binding for the Node.js HTTP parser, and it’s built in C.

By just installing httptools, you can achieve a performance improvement!

First, install httptools:
```bash
pip install httptools
```

Then, use httptools with Uvicorn:
```bash
uvicorn main:app --http httptools
```

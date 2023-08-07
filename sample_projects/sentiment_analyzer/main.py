from typing import Dict

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from .classifier.model import Model, get_model

app = FastAPI()


class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    probabilities: Dict[str, float]
    sentiment: str
    confidence: float

# Start up event
@app.on_event("startup")
async def startup():
    import gc

    # PyTorch internally uses a lot of private objects, which activates the garbage collector.
    # To avoid the garbage collector to be activated, we freeze the garbage collector.
    # This will put the references of the PyTorch objects to the permanent generation, which is not cleaned by the garbage collector.
    gc.freeze()


@app.post("/predict", response_model=SentimentResponse)
def predict(request: SentimentRequest, model: Model = Depends(get_model)):
    sentiment, confidence, probabilities = model.predict(request.text)
    return SentimentResponse(
        sentiment=sentiment, confidence=confidence, probabilities=probabilities
    )

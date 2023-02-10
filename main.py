import os
from fastapi import FastAPI
from converter_1 import Converter
from model_requests import RequestAddress


app = FastAPI()


@app.post("/address-extractor/{addess}")
async def address(payload: RequestAddress):
    inputs = payload.dict()["text"]
    converter = Converter(inputs=inputs, pid=int(os.getpid()), info="address")
    data = converter.convert()
    return {"parsed_outputs": data}


@app.get("/intent-extractor/{intent}")
async def intent(tweet: str):
    return {"intent": tweet}

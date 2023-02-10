from typing import List
import os
import logging
import openai

from fastapi import FastAPI
from reqs import RequestAddress
from reqs import RequestIntent

import converter

from functools import lru_cache

from fastapi import Depends, FastAPI

from config import Settings

from pydantic import BaseModel, Field

app = FastAPI()


class RequestAddress(BaseModel):
    inputs: List[str] = Field(
        description="list of tweets to classify or parse",
        default=""" ["İskenderun Hatay Mustafa Kemal mahallesi 544 sokak no:11 (Batı Göz hastanesi sokağı) Selahattin Yurt Dudu Yurt Sezer Yurt GÖÇÜK ALTINDALAR!!! #DEPREMOLDU #depremhatay #deprem #Hatay #hatayacil #HatayaYardım #hataydepremi", "LÜTFEN YAYIN!!!! 8 katlı bina HATAYDA Odabaşı mah. Uğur Mumcu caddesi no 4 Mahmut Karakaş kat 4"]""",
    )


class RequestIntent(BaseModel):
    inputs: List[str] = Field(
        description="list of tweets to classify or parse",
        default=""" ["İskenderun Hatay Mustafa Kemal mahallesi 544 sokak no:11 (Batı Göz hastanesi sokağı) Selahattin Yurt Dudu Yurt Sezer Yurt GÖÇÜK ALTINDALAR!!! #DEPREMOLDU #depremhatay #deprem #Hatay #hatayacil #HatayaYardım #hataydepremi", "LÜTFEN YAYIN!!!! 8 katlı bina HATAYDA Odabaşı mah. Uğur Mumcu caddesi no 4 Mahmut Karakaş kat 4"]""",
    )


def setup_openai(worker_id: int = 0):
    try:
        openai_keys = os.getenv("OPENAI_API_KEY_POOL").split(",")
    except KeyError:
        logging.error("OPENAI_API_KEY_POOL environment variable is not specified")

    assert len(openai_keys) > 0, "No keys specified in the environment variable"

    logging.warning(f"worker id in open ai keys {worker_id}")
    worker_openai_key = openai_keys[worker_id % len(openai_keys)].strip()
    openai.api_key = worker_openai_key


def setup_geocoding(worker_id: int = 0):
    try:
        geo_keys = os.getenv("GEO_KEY_POOL").split(",")
    except KeyError:
        logging.error("GEO_KEY_POOL environment variable is not specified")

    assert len(geo_keys) > 0, "No keys specified in the environment variable"

    worker_geo_key = geo_keys[worker_id % len(geo_keys)].strip()

    return worker_geo_key


@lru_cache()
def get_settings():
    settings = Settings()

    with open(settings.address_prompt_file) as handle:
        settings.address_template = handle.read()

    with open(settings.intent_prompt_file) as handle:
        settings.intent_template = handle.read()

    if settings.geo_location:
        settings.geo_key = setup_geocoding()

    pid = int(os.getpid())
    setup_openai(pid % settings.num_workers)

    logging.warning(f"Engine {settings.engine}")

    return settings


def convert(
    info: str,
    inputs: List[str],
    template: str,
    settings: Settings,
):
    if info == "address":
        template = settings.address_template
        max_tokens = settings.address_max_tokens
        temperature = 0.1
        frequency_penalty = 0.3
    elif info == "intent":
        template = settings.intent_template
        max_tokens = settings.intent_max_tokens
        temperature = 0.0
        frequency_penalty = 0.0
    else:
        raise ValueError("Unknown info")

    text_inputs = []
    for tweet in inputs:
        text_inputs.append(template.format(ocr_input=tweet))
    outputs = converter.query_with_retry(
        text_inputs,
        engine=settings.engine,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=frequency_penalty,
        presence_penalty=0,
        stop="#END",
    )

    returned = []
    for output in outputs:
        returned_dict = {}
        returned_dict["string"] = output
        try:
            returned_dict["processed"] = converter.postprocess(info, output[0])
        except Exception as e:
            returned_dict["processed"] = {}
            logging.warning(f"Parsing error in {output},\n {e}")

        if info == "address" and settings.geo_location and returned_dict["processed"]:
            returned_dict["processed"]["geo"] = converter.get_geo_result(
                settings.geo_key, returned_dict["processed"]
            )
        returned.append(returned_dict)

    return returned


@app.post("/address-extractor")
async def address(payload: RequestAddress):
    settings = get_settings()
    inputs = payload.dict()["inputs"]
    outputs = convert("address", inputs, settings.address_template, settings)
    return {"outputs": outputs}


@app.post("/intent-extractor/")
async def intent(payload: RequestIntent):
    settings = get_settings()
    inputs = payload.dict()["inputs"]
    outputs = convert("intent", inputs, settings.address_template, settings)
    return {"outputs": outputs}

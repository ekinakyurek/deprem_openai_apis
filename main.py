import logging
import os
from functools import lru_cache
from typing import List
import openai
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
import converter
from config import Settings
from models import IntentResponse, RequestIntent

app = FastAPI()

@lru_cache()
def get_settings():
    settings = Settings()

    with open(settings.address_prompt_file) as handle:
        settings.address_template = handle.read()

    # with open(settings.intent_prompt_file) as handle:
    #     settings.intent_template = handle.read()

    # with open(settings.detailed_intent_prompt_file) as handle:
    #     settings.detailed_intent_template = handle.read()

    with open(settings.detailed_intent_prompt_file_v2) as handle:
        settings.detailed_intent_template_v2 = handle.read()

    if settings.geo_location:
        settings.geo_key = converter.setup_geocoding()

    converter.setup_openai(int(os.getpid()) % settings.num_workers)

    logging.warning(f"Engine {settings.engine}")

    return settings


def convert(
    info: str,
    inputs: List[str],
    settings: Settings,
):
    if info == "address":
        template = settings.address_template
        max_tokens = settings.address_max_tokens
        temperature = 0.1
        frequency_penalty = 0.3
    # elif info == "intent":
    #     template = settings.intent_template
    #     max_tokens = settings.intent_max_tokens
    #     temperature = 0.0
    #     frequency_penalty = 0.0
    # elif info == "detailed_intent":
    #     template = settings.detailed_intent_template
    #     max_tokens = settings.detailed_intent_max_tokens
    #     temperature = 0.0
    #     frequency_penalty = 0.0
    elif info == "detailed_intent_v2":
        template = settings.detailed_intent_template_v2
        max_tokens = settings.detailed_intent_max_tokens_v2
        temperature = 0.0
        frequency_penalty = 0.0
    else:
        raise ValueError("Unknown information extraction requested")

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
            returned_dict["processed"] = {
                "intent": [""],
                "detailed_intent_tags": [""],
            }
            logging.warning(f"Parsing error in {output},\n {e}")

        if info == "address" and settings.geo_location and returned_dict["processed"]:
            returned_dict["processed"]["geo"] = converter.get_geo_result(
                settings.geo_key, returned_dict["processed"]
            )
        returned.append(returned_dict)

    return returned


@app.post("/intent-extractor/", response_model=IntentResponse)
async def intent(payload: RequestIntent):
    try:
        settings = get_settings()
        inputs = payload.dict()["inputs"]
        outputs = convert("detailed_intent_v2", inputs, settings)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")

    return {"response": outputs}

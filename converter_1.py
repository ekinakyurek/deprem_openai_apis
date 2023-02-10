import json
import logging
import os
import random
import re
import time
import urllib
import openai
import model_requests


GEO_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json?"
NON_ADDRESS_WORDS = [
    "arkadaş",
    "bebek",
    "enkaz",
    "deprem",
    "ekipman",
    "araç",
    "kayıp",
    "acil",
    "yardım",
    "kurtarma",
    "kayıp",
    "aile",
    "baba",
]


class Converter:
    def __init__(
        self,
        inputs,
        pid,
        info,
        prompt_file="prompts/address.txt",
        max_tokens=384,
        batch_size=20,
        geo_location=False,
        engine="code-cushman-001",
    ):
        # These are the list of tweets that we will be converting
        self.input: list[str] = inputs
        # Choose an openai/geo key using the seed as the pid. This is a hacky solution to distribute the load by keys
        # I wanted to use this but couldnt get it to work: https://uwsgi-docs.readthedocs.io/en/latest/API.html
        self.seed: int = pid
        self.max_tokens: int = max_tokens
        self.batch_size: int = batch_size
        self.geo_location: bool = geo_location
        self.engine: str = engine
        self.prompt_file = "prompts/address.txt"
        self.info = info

        # Set the openai key
        try:
            openai_keys = os.environ["OPENAI_API_KEY_POOL"].split(",")
        except KeyError:
            logging.error("OPENAI_API_KEY_POOL environment variable is not specified")
        random.seed(self.seed)
        # The pid(worker) will be used as a seed to choose a key from the pool of keys
        worker_openai_key = random.choice(openai_keys)
        openai.api_key = worker_openai_key
        # Set the geo key

        try:
            geo_keys = os.environ["GEO_KEY_POOL"].split(",")
        except KeyError:
            logging.error("GEO_KEY_POOL environment variable is not specified")
        self.geo_key = random.choice(geo_keys)

    def postprocess_for_address(self, address):
        # a quick rule based filtering for badly parsed outputs.
        address = json.loads(address)
        if type(address) == dict:
            for key in (
                "mahallesi | bulvarı",
                "sokak | caddesi | yolu",
                "sitesi | apartmanı",
                "no | blok",
                "kat",
                "phone",
            ):
                if (
                    key in address
                    and len(address[key]) > 50
                    or any(word in address[key] for word in NON_ADDRESS_WORDS)
                ):
                    address[key] = ""

            for key in ("no | blok", "kat"):
                if key in address and len(address[key]) > 20:
                    address[key] = ""

        return address

    def postprocess_for_intent(self, intent):
        m = re.search(r"(?<=\[).+?(?=\])", intent)
        if m:
            return {"intent": m.group()}
        else:
            return {"intent": "unknown"}

    def postprocess(self, info, line):
        if info == "address":
            return self.postprocess_for_address(line)
        elif info == "intent":
            return self.postprocess_for_intent(line)
        else:
            raise ValueError("Unknown info type")

    def get_address_str(self, address):
        address_str = ""
        for key in (
            "mahallesi | bulvarı",
            "sokak | caddesi | yolu",
            "sitesi | apartmanı",
            "no | blok",
            "city",
            "province",
        ):
            address_str += address.get(key, "") + " "

        return address_str.strip()

    def query_with_retry(self, inputs, max_retry=5):
        """Queries GPT API up to max_retry time to get the responses."""
        request_completed = False
        current_retry = 0
        outputs = [['{"status": "ERROR"}']] * len(inputs)
        while not request_completed and current_retry <= max_retry:
            try:
                response = openai.Completion.create(
                    engine=self.engine,
                    prompt=inputs,
                    temperature=0.1,
                    max_tokens=self.max_tokens,
                    top_p=1,
                    frequency_penalty=0.3,
                    presence_penalty=0,
                    stop="#END",
                )
                current_outputs = response["choices"]
                outputs = []
                for i in range(len(current_outputs)):
                    outputs.append(
                        [
                            line
                            for line in current_outputs[i]["text"].split("\n")
                            if len(line) > 10
                        ]
                    )
                request_completed = True
                logging.info("request completed")
            except openai.error.RateLimitError as error:
                logging.warning(f"Rate Limit Error: {error}")
                # wait for token limit in the API
                time.sleep(10 * current_retry)
                current_retry += 1
            except openai.error.InvalidRequestError as error:
                logging.warning(f"Invalid Request: {error}")
                # wait for token limit in the API
                time.sleep(10 * current_retry)
                current_retry += 1
        return outputs

    def get_geo_result(self, key, address):
        address_str = self.get_address_str(address)
        parameters = {"address": address_str, "key": key}
        response = model_requests.get(
            f"{GEO_BASE_URL}{urllib.parse.urlencode(parameters)}"
        )

        if response.status_code == 200:
            results = json.loads(response.content)["results"]
            if results:
                for result in results:
                    if "geometry" in result and "location" in result["geometry"]:
                        loc = result["geometry"]["location"]
                        link = "https://maps.google.com/?q={lat},{lng}".format(
                            lat=loc["lat"], lng=loc["lng"]
                        )
                        result["gmaps_link"] = link
            return results
        else:
            logging.warning(response.content)

    def convert(self):
        with open(self.prompt_file) as f:
            template = f.read()
        text_inputs = []
        for prompt in self.input:
            text_inputs.append(template.format(ocr_input=prompt))
        outputs = self.query_with_retry(text_inputs)
        returned = []
        for output in outputs:
            print("this is the output")
            print(output)
            print("this is the output")
            returned_dict = {}
            returned_dict["string"] = output
            try:
                returned_dict["processed"] = self.postprocess(self.info, output[0])
            except Exception as e:
                returned_dict["processed"] = {}
                logging.warning(f"Parsing error in {output},\n {e}")
            if (
                self.info == "address"
                and self.geo_location
                and returned_dict["processed"] == dict
            ):
                returned_dict["geo"] = self.get_geo_result(
                    self.geo_key, returned_dict["processed"]
                )
            returned.append(returned_dict)
        return returned

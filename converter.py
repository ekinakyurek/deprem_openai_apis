import json
import os
import re
import urllib
from typing import List
import openai
import requests
from absl import app, flags, logging
from tqdm import tqdm
from network_manager import interact_with_api


FLAGS = flags.FLAGS

flags.DEFINE_string(
    "prompt_file", default=None, help="Prompt file to use for the problem"
)

flags.DEFINE_string("input_file", default=None, help="Input file to read data")

flags.DEFINE_string("output_file", default=None, help="Output file to write to")

flags.DEFINE_integer("max_tokens", default=384, help="LM max generation length")

flags.DEFINE_integer("worker_id", default=0, help="Worker id for the job")

flags.DEFINE_integer("num_workers", default=1, help="number of workers")

flags.DEFINE_integer("batch_size", default=20, help="batch size for OpenAI queries")

flags.DEFINE_boolean(
    "geo_location", default=False, help="whether to add geo location to the output"
)

flags.DEFINE_string("info", default="address", help="address | intent")

flags.DEFINE_string("engine", "code-davinci-002", help="GPT engines")

GEO_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json?"

# TODO: add more keywords.
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


def postprocess_for_address(address):
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


TAG_MAP = {
    "ELECTRONICS": "Elektronik",
    "WATER": "Su",
    "LOGISTICS": "Lojistik",
    "TRANSPORTATION": "Lojistik",
    "FOOD": "Yemek",
    "RESCUE": "Kurtarma",
    "HEALTH": "Saglik",
    "UNINFORMATIVE": "Alakasiz",
    "SHELTER": "Barinma",
    "LOOTING": "Yagma",
    "CLOTHES": "Giysi",
}


def postprocess_for_intent(intent):
    m = re.search(r"(?<=\[).+?(?=\])", intent)
    if m:
        tags = m.group()
        tags = [TAG_MAP.get(tag.strip(), tag.strip()) for tag in tags.split(",")]
        return {"intent": ",".join(tags)}
    else:
        return {"intent": "Diğer"}


def postprocess_for_intent_v2(intent):
    m = re.findall(r"(?<=\[).+?(?=\])", intent)
    if m and len(m) == 2:
        detailed_intent, intent = m

        detailed_intent_tags = [
            TAG_MAP.get(tag.strip(), tag.strip()) for tag in detailed_intent.split(",")
        ]
        intent_tags = [
            TAG_MAP.get(tag.strip(), tag.strip()) for tag in intent.split(",")
        ]

        return {
            "intent": intent_tags,  # ",".join(intent_tags),
            "detailed_intent_tags": detailed_intent_tags,  # ",".join(detailed_intent_tags),
        }
    else:
        return {
            "intent": [""],  # ",".join(intent_tags),
            "detailed_intent_tags": [""],  # ",".join(detailed_intent_tags),
        }


def postprocess(info, line):
    if info == "address":
        return postprocess_for_address(line)
    elif info == "intent":
        return postprocess_for_intent(line)
    elif info == "detailed_intent":
        return postprocess_for_intent(line)
    elif info == "detailed_intent_v2":
        return postprocess_for_intent_v2(line)
    else:
        raise ValueError("Unknown info type")


def get_address_str(address):
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


def query_with_retry(inputs: List[str], **kwargs) -> List[List[str]]:
    """Queries GPT API up to max_retry time to get the responses."""

    try:
        response = interact_with_api(openai.Completion.create, prompt=inputs, **kwargs)
    except Exception:
        # TODO can main method handle this output?
        return [['{"status": "ERROR"}']] * len(inputs)

    return [
        [line for line in choice["text"].split("\n") if len(line) > 10]
        for choice in response["choices"]
    ]


def setup_openai(worker_id: int = 0):
    logging.warning(f"worker id in open ai keys {worker_id}")

    try:
        openai_keys = os.getenv("OPENAI_API_KEY_POOL").split(",")
    except KeyError:
        logging.error(
            "OPENAI_API_KEY_POOL or OPENAI_API_BASE_POOL environment variable is not"
            " specified"
        )

    assert len(openai_keys) > 0, "No keys specified in the environment variable"

    openai.api_key = openai_keys[worker_id % len(openai_keys)].strip()

    try:
        openai_bases = os.getenv("OPENAI_API_BASE_POOL").split(",")
        assert len(openai_bases) == len(openai_keys)
        openai.api_type = "azure"
        openai.api_version = "2022-12-01"
        openai.api_base = openai_bases[worker_id % len(openai_bases)].strip()
    except KeyError:
        logging.warning("OPENAI_API_BASE_POOL is not specified in the environment")
    except AssertionError as msg:
        logging.error(
            "Env variables OPENAI_API_KEY_POOL and OPENAI_API_BASE_POOL has"
            f" incosistent shapes, {msg}"
        )


def setup_geocoding(worker_id: int = 0):
    try:
        geo_keys = os.getenv("GEO_KEY_POOL").split(",")
    except KeyError:
        logging.error("GEO_KEY_POOL environment variable is not specified")

    assert len(geo_keys) > 0, "No keys specified in the environment variable"

    worker_geo_key = geo_keys[worker_id % len(geo_keys)].strip()

    return worker_geo_key


def get_geo_result(key, address):
    address_str = get_address_str(address)
    parameters = {"address": address_str, "key": key}
    response = requests.get(f"{GEO_BASE_URL}{urllib.parse.urlencode(parameters)}")

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


def main(_):
    setup_openai(FLAGS.worker_id)
    if FLAGS.geo_location:
        geo_key = setup_geocoding(FLAGS.worker_id)

    with open(FLAGS.prompt_file) as handle:
        template = handle.read()

    if FLAGS.info == "address":
        completion_params = dict(temperature=0.1, frequency_penalty=0.3)
    elif "intent" in FLAGS.info:
        completion_params = dict(temperature=0.0, frequency_penalty=0.0)
    else:
        raise ValueError("Unknown info")

    logging.info(f"Engine {FLAGS.engine}")
    with open(FLAGS.input_file) as handle:
        # raw_data = [json.loads(line.strip()) for line in handle]
        raw_data = json.load(handle)
        split_size = len(raw_data) // FLAGS.num_workers
        raw_data = raw_data[
            FLAGS.worker_id * split_size : (FLAGS.worker_id + 1) * split_size
        ]

    logging.info(f"Length of the data for this worker is {len(raw_data)}")
    text_inputs = []
    raw_inputs = []

    for index, row in tqdm(enumerate(raw_data)):
        # text_inputs.append(template.format(ocr_input=row["Tweet"]))
        text_inputs.append(template.format(ocr_input=row["text_cleaned"]))
        raw_inputs.append(row)

        if (index + 1) % FLAGS.batch_size == 0 or index == len(raw_data) - 1:
            outputs = query_with_retry(
                text_inputs,
                engine=FLAGS.engine,
                max_tokens=FLAGS.max_tokens,
                top_p=1,
                presence_penalty=0,
                stop="#END",
                **completion_params,
            )

            with open(FLAGS.output_file, "a+") as handle:
                for inp, output_lines in zip(raw_inputs, outputs):
                    # for output_line in output_lines:
                    output_line = output_lines[0]
                    current_input = inp.copy()
                    try:
                        current_input[FLAGS.info + "_json"] = postprocess(
                            FLAGS.info, output_line
                        )
                        current_input[FLAGS.info + "_str"] = output_line
                    except Exception as e:
                        logging.warning(f"Parsing error in {output_line},\n {e}")
                        current_input[FLAGS.info + "_json"] = {}
                        current_input[FLAGS.info + "_str"] = output_line

                    if (
                        FLAGS.info == "address"
                        and FLAGS.geo_location
                        and type(current_input[FLAGS.info + "_json"]) == dict
                    ):
                        current_input["geo"] = get_geo_result(
                            geo_key, current_input[FLAGS.info + "_json"]
                        )

                    json_output = json.dumps(current_input)
                    handle.write(json_output + "\n")

            text_inputs = []
            raw_inputs = []


if __name__ == "__main__":
    app.run(main)

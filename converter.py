import json
import os
import openai
from absl import app
from absl import flags
from absl import logging
import time
from tqdm import tqdm



# openai.organization = os.getenv("OPENAI_API_ORGANIZATION")

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "prompt_file", default=None, help="Prompt file to use for the problem"
)

flags.DEFINE_string("input_file", default=None, help="Input file to read data")

flags.DEFINE_string("key_file", default=None, help="Openai key file")

flags.DEFINE_string("output_file", default=None, help="Output file to write to")

flags.DEFINE_integer("max_tokens", default=400, help="LM max generation length")

flags.DEFINE_string("engine", "code-davinci-002", help="GPT engines")


def query_with_retry(inputs, max_retry=30):
    """Queries GPT API up to max_retry time to get the responses."""
    request_completed = False
    current_retry = 0
    outputs = [['{"status": "ERROR"}']] * len(inputs)
    while not request_completed and current_retry <= max_retry:
        try:
            response = openai.Completion.create(
                engine=FLAGS.engine,
                prompt=inputs,
                temperature=0,
                max_tokens=FLAGS.max_tokens,
                top_p=1,
                frequency_penalty=0,
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
        except Exception as e:
            logging.warning(f"Error: {e}")
            # wait for token limit in the API
            time.sleep(10)
            current_retry += 1
    return outputs


def main(_):
    openai.api_key = [el for el in open(FLAGS.key_file, "r")][0][:-1]
    
    with open(FLAGS.prompt_file) as handle:
        template = handle.read()
    # extract tweets from third columns
    # raw_data = pd.read_csv(FLAGS.input_file)

    with open(FLAGS.input_file) as handle:
        raw_data = json.load(handle)["hits"]["hits"]
        # raw_data = [json.loads(line)["input"] for line in handle]

    logging.info(f"Length of the data is {len(raw_data)}")
    text_inputs = []
    raw_inputs = []

    # if os.file.exists(FLAGS.output_file):
    #     os.error("Output file exists!")

    for index, row in tqdm(enumerate(raw_data)):
        # third columns is the tweet?
        text_inputs.append(template.format(ocr_input=row["_source"]["text"]))
        raw_inputs.append(row)

        if (index + 1) % 20 == 0 or index == len(raw_data) - 1:
            outputs = query_with_retry(text_inputs)
            with open(FLAGS.output_file, "a+") as handle:
                for inp, addresses in zip(raw_inputs, outputs):
                    for address in addresses:
                        current_input = inp.copy()
                        try:
                            current_input["address_json"] = json.loads(address)
                            current_input["address_str"] = ""
                        except Exception as e:
                            logging.warning(f"Parsing error in {address},\n {e}")
                            current_input["address_json"] = {}
                            current_input["address_str"] = address

                        json_output = json.dumps(current_input)
                        handle.write(json_output + "\n")


if __name__ == "__main__":
    app.run(main)

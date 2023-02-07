import json
import os
import openai
from absl import app
from absl import flags
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

openai.organization = os.getenv("OPENAI_API_ORGANIZATION")

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "prompt_file", default=None, help="Prompt file to use for the problem"
)

flags.DEFINE_string("input_file", default=None, help="Input file to read data")

flags.DEFINE_string("output_file", default=None, help="Output file to write to")

flags.DEFINE_integer("max_tokens", default=400, help="LM max generation length")

flags.DEFINE_string("engine", "code-davinci-002", help="GPT engines")


def query_with_retry(inputs, max_retry=2):
    """Queries GPT API up to max_retry time to get the responses."""
    request_completed = False
    current_retry = 0
    outputs = ["ERROR"] * len(inputs)
    while not request_completed and current_retry <= 2:
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
                for line in current_outputs[i]["text"].split("\n"):
                    outputs.append(line)
            request_completed = True
        except Exception as e:
            print("Error:", e)
            # wait for token limit in the API
            time.sleep(30)
    return outputs


def main(_):
    with open(FLAGS.prompt_file) as handle:
        template = handle.read()

    with open(FLAGS.input_file) as handle:
        raw_data = [json.loads(line)["input"] for line in handle]

    current_inputs = []
    processed_data = []
    for i, datum in enumerate(raw_data):
        current_inputs.append(template.format(ocr_input=datum))
        if (i + 1) % 20 == 0 or i == len(raw_data) - 1:
            current_outputs = query_with_retry(current_inputs)
            processed_data += current_outputs
            current_inputs = []

    with open(FLAGS.output_file, "w") as handle:
        for out in processed_data:
            handle.write(out + "\n")


if __name__ == "__main__":
    app.run(main)

import json
from absl import flags
from absl import app

FLAGS = flags.FLAGS
flags.DEFINE_string("input_file", default=None, help="Input file to read data")
flags.DEFINE_string("key_num", default=None, help="number of splits")
flags.DEFINE_string("output_dir", default=None, help="Output file to write to")

def split(_):
    # Read the json file
    with open(FLAGS.input_file, "r") as f:
        data = json.load(f)

    # Get data['hits']['hits'], split it into key_num parts
    # and write each part to a json file
    hits = data['hits']['hits']
    key_num = int(FLAGS.key_num)
    split_size = len(hits) // key_num
    for i in range(key_num):
        with open(f'{FLAGS.output_dir}/{i+1}.json', 'w') as f:
            json.dump({"hits":{"hits":hits[i*split_size:(i+1)*split_size]}}, f)
    

if __name__ == "__main__":
    app.run(split)
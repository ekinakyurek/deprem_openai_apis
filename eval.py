import json
import numpy as np
import sklearn
import sklearn.metrics
from sklearn.preprocessing import MultiLabelBinarizer
import pdb
from absl import app, flags, logging
from tqdm import tqdm
import pdb

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "input_file", default=None, help="Prompt file to use for the problem"
)

def main(_):
    true_values = []
    pred_values = []

    FILE_NAME = FLAGS.input_file
    with open(FILE_NAME.replace("jsonl", "tsv"), "w") as handle:

        for line in open(FILE_NAME):
            datum = json.loads(line)
            y_true = datum['labels']
            y_pred = datum['detailed_intent_v2_json']['intent'].split(',')
            true_values.append(y_true)
            pred_values.append(y_pred)
            print(datum['text'].replace('\n', ''), "\t", y_true, "\t", y_pred, file=handle)
        
        
    binarizer = MultiLabelBinarizer().fit(true_values)

    # pdb.set_trace()
    true_values = binarizer.transform(true_values)
    pred_values = binarizer.transform(pred_values)


    # pdb.set_trace()
    print(sklearn.metrics.classification_report(true_values, pred_values, target_names =binarizer.classes_))


if __name__ == "__main__":
    app.run(main)
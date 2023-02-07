#!/bin/bash -l

NUMKEY=5
BASE_PATH="/project/llamagrp/feyza/address_parser/output"
INPUTFILE="data/data.json"

# First split data into separate files
python data_split.py --input_file $INPUTFILE --key_num $NUMKEY --output_dir data

# Then run the converter
for i in {1..5}
do
    EXPERIMENT_NAME="key_${i}"
    OUTPUT_PATH=$BASE_PATH/$EXPERIMENT_NAME
    mkdir -p $OUTPUT_PATH
    python converter.py \
    --prompt_file prompts/main.txt \
    --input_file data/${i}.json \
    --output_file $OUTPUT_PATH/output.jsonl \
    --key_file keys/openai_key_${i} > $OUTPUT_PATH/out.log 2>&1 &
done



#!/bin/bash
EXP_NAME="2k"
NUMKEY=5
BASE_PATH="/home/akyurek/gpt3-arithmetic/"
INPUTFILE="data/data.json"

# First split data into separate files
mkdir -p data/${EXP_NAME}/
python data_split.py --input_file $INPUTFILE --key_num $NUMKEY --output_dir data/${EXP_NAME}/

# Then run the converter
for i in {1..5}
do
    OUTPUT_PATH=$BASE_PATH/exps/${EXP_NAME}/${i}/
    mkdir -p $OUTPUT_PATH
    python converter.py \
    --prompt_file prompts/main.txt \
    --input_file data/${EXP_NAME}/${i}.json \
    --output_file $OUTPUT_PATH/output.jsonl \
    --key_file keys/openai_key_${i} > $OUTPUT_PATH/out.log 2>&1 &
done



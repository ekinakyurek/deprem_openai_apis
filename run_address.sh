#!/bin/bash
EXP_NAME="address/"
BASE_PATH="/home/akyurek/deprem/"
INPUTFILE="data/test.jsonl"
NUMKEY=5

# # First split data into separate files
# mkdir -p data/${EXP_NAME}/
# python data_split.py --input_file $INPUTFILE --key_num $NUMKEY --output_dir data/${EXP_NAME}/

# Then run the converter


for i in $(seq 0 $((NUMKEY-1)));
do
    OUTPUT_PATH=$BASE_PATH/exps/${EXP_NAME}/${i}/
    mkdir -p $OUTPUT_PATH
    python converter.py \
    --prompt_file prompts/main.txt \
    --input_file $INPUTFILE \
    --output_file $OUTPUT_PATH/output.jsonl \
    --worker_id $i \
    --geo_location \
    --info="address" \
    --num_workers $NUMKEY > $OUTPUT_PATH/out.log 2>&1 &
done



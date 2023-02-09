#!/bin/bash
EXP_NAME="intent_test"
BASE_PATH="/home/akyurek/deprem/"
INPUTFILE="data/test.jsonl"
NUMKEY=5

for i in $(seq 0 $((NUMKEY-1)));
do
    OUTPUT_PATH=$BASE_PATH/exps/${EXP_NAME}/${i}/
    mkdir -p $OUTPUT_PATH
    python converter.py \
    --prompt_file prompts/intent.txt \
    --input_file $INPUTFILE \
    --output_file $OUTPUT_PATH/output.jsonl \
    --worker_id $i \
    --info="intent" \
    --num_workers $NUMKEY > $OUTPUT_PATH/out.log 2>&1 &
done



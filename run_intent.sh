#!/bin/bash
EXP_NAME="detailed_intent_w_categories"
BASE_PATH="/home/akyurek/deprem/"
INPUTFILE="data/intent-multilabel-test-v1-2.json"
NUMKEY=5

for i in $(seq 0 $((NUMKEY-1)));
do
    OUTPUT_PATH=$BASE_PATH/exps/${EXP_NAME}/${i}/
    mkdir -p $OUTPUT_PATH
    python converter.py \
    --prompt_file prompts/intent_v5_categories.txt \
    --input_file $INPUTFILE \
    --output_file $OUTPUT_PATH/output.jsonl \
    --worker_id $i \
    --info="detailed_intent_v2" \
    --max_tokens 100 \
    --num_workers $NUMKEY > $OUTPUT_PATH/out.log 2>&1 &
done



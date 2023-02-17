#!/bin/bash
source setup.sh
EXP_NAME="new_labels_code_davinci_v4"
BASE_PATH="/home/akyurek/git/deprem/"
#INPUTFILE="data/intent-multilabel-test-v1-2.json"
INPUTFILE="data/testv1.3.json"
NUMKEY=4
EXP_FOLDER=$BASE_PATH/exps/${EXP_NAME}/

echo "deleting ${EXP_FOLDER}"

# rm -rf $EXP_FOLDER

# for i in $(seq 0 $((NUMKEY-1)));
# do
#     OUTPUT_PATH=$EXP_FOLDER/${i}/
#     mkdir -p $OUTPUT_PATH
#     python src/converter.py \
#     --prompt_file prompts/detailed_intent.txt \
#     --input_file $INPUTFILE \
#     --output_file $OUTPUT_PATH/output.jsonl \
#     --worker_id $i \
#     --info="detailed_intent" \
#     --max_tokens 100 \
#     --engine="code-davinci-002" \
#     --num_workers $NUMKEY > $OUTPUT_PATH/out.log 2>&1 &
# done

cat $EXP_FOLDER/**/output.jsonl > $EXP_FOLDER/merged.jsonl
python eval.py --input_file $EXP_FOLDER/merged.jsonl

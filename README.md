# Address Extractor

The code extracts and parses adresses from raw tweets via OpenAI GPT Codex API by using few-shot prompting.

# How To Run

Currently input format is `.jsonl` with `{"input": tweet_text}`, see an example input file here [data/](./data/)

- Run the converter
```
python converter.py --prompt_file prompts/main.txt --input_file data/test.jsonl --output_file output.jsonl --key_file PATH_TO_KEY
```
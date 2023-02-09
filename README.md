# Address Extractor

The code can extract adresses from raw Turkiye earthquake tweets and classify them for intent via OpenAI GPT Codex API by using few-shot prompting.

# How To Run

Currently the input format is `.jsonl` where each line has a json string with "Tweet" field, see an example input file here [data/test.jsonl](./data/test.jsonl).

Export two environment variables as comma seperated keys:

```SHELL
export OPENAI_API_KEY_POOL=key1,key2,key3...
export GEO_KEY_POOL=key1,key2
```

- Specify your paths in [run_addres.sh](./run_address.sh)), then run the script
```SHELL
./run_address.sh
```

- Specify your paths in [run_intent.sh](./run_intent.sh)), then run the script.
```SHELL
./run_intent.sh
```
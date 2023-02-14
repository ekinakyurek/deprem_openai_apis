# Address and Intent Extractor

> Please use the active remote: https://github.com/acikkaynak/deprem_openai_apis

> Prompts in this repo are placeholder for the privacy reasons. Please contact us if you'd like to obtain them.

The code can extract adresses from raw Turkiye earthquake tweets and classify them for intent via OpenAI GPT Codex API by using few-shot prompting.

# How To Run

Currently the input format is `.jsonl` where each line has a json string with "Tweet" field, see an example input file here [data/test.jsonl](./data/test.jsonl).

Export two environment variables as comma seperated keys:

```SHELL
export OPENAI_API_KEY_POOL=key1,key2,key3...
export GEO_KEY_POOL=key1,key2
```

optionally for afet org api base urls
```SHELL
export OPENAI_API_BASE_POOL=
```

To extract the geo location address information:
- Specify your paths in [run_addres.sh](./run_address.sh), then run the script
```SHELL
./run_address.sh
```

To extract the intent information:
- Specify your paths in [run_intent.sh](./run_intent.sh), then run the script.
```SHELL
./run_intent.sh
```

# To Run FastAPI Backend

- To run locally `uvicorn main:app --reload`



Running github actions 

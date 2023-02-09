# Address and Intent Extractor

The code can extract adresses from raw Turkiye earthquake tweets and classify them for intent via OpenAI GPT Codex API by using few-shot prompting.

# How To Run

Currently the input format is `.jsonl` where each line has a json string with "Tweet" field, see an example input file here [data/test.jsonl](./data/test.jsonl).

Export two environment variables as comma seperated keys:

```SHELL
export OPENAI_API_KEY_POOL=key1,key2,key3...
export GEO_KEY_POOL=key1,key2
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

# Validator Example
This is a simple example of how the llm output could be validated. `cities_data.json` contains the provinces and the cities in each province. As the tweets could contain typos, the llm could copy the incorrect city/province to the output.
## Example of incorrect LLM output due to a typo in the text
`Incorrect province Input`
```
"RT @ukkuli: ACİL!!!
İkendern htayy
mustfa Kmal mahallesi 544 sokak no:11 (Batı Göz hastanesi sokağı)

Selahattin Yurt
Dudu Yurt
Sezer Yurt
GÖÇÜK ALTINDALAR!!!
#DEPREMOLDU #depremhatay #deprem #Hatay #hatayacil #HatayaYardım #hataydepremi"
```
`Output`
```
{{"province": "htayy", "city": "İkendern", "mahallesi | bulvarı": "Mustafa Kemal Mahallesi", "sokak | caddesi | yolu": "544 Sokak", "no | blok": "11", "sitesi | apartmanı":"" ,"phone": "", "isimler": "Selahattin Yurt, Dudu Yurt, Sezer Yurt"}}
```

Although these mistakes could be avoided if a list of provinces and cities are provided in the input. But, as we scale to the neighbourhoods and streets, this could be costly. (The current `main.txt` contains a list of provinces.)

## Levenshtein distance
- We will use Levenshtein dist to get the closest province and city from the llm_output
- We will then validate whether the city is in the province or not. With a better database this could be granulized to neighbourhoods and streets.

``` python
llm_output = """{"province": "Hatay", "city": "zeytinburnu", "mahallesi | bulvarı": "Mustafa Kemal Mahallesi", "sokak | caddesi | yolu": "544 Sokak", "no | blok": "11", "sitesi | apartmanı":"" ,"phone": "", "isimler": "Selahattin Yurt, Dudu Yurt, Sezer Yurt"}"""
a = Validator(
    data_path="cities_data.json",
    llm_output=llm_output,
)
```
`output`: `False`
Zeytinburnu is not in Hatay!
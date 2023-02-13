from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("gpt2")


class GPTTokenizer:
    MAX_TOKENS = 2047

    @classmethod
    def token_count(cls, text: str) -> int:
        return len(tokenizer(text, truncation=False)["input_ids"])

    @classmethod
    def truncate(self, text: str, max_tokens: int) -> str:
        encoded = tokenizer(text, truncation=True, max_length=max_tokens)
        return tokenizer.decode(encoded["input_ids"])

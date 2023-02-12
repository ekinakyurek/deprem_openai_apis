local-test:
	docker build -t deprem-openai-apis-test:latest .
	docker run --rm -t deprem-openai-apis-test:latest sh -c "OPENAI_API_BASE_POOL=${OPENAI_API_BASE_POOL} OPENAI_API_KEY_POOL=${OPENAI_API_KEY_POOL} pytest --verbose"

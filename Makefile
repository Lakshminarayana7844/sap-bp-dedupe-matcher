.PHONY: run test docker

run:             ## dedupe the sample data into ./out
	python -m src.matcher.pipeline --input data/business_partners.csv --out out/

test:            ## 19 pure-python tests
	python -m pytest tests/ -q

docker:          ## run inside Docker
	docker build -t sap-bp-dedupe-matcher .
	docker run --rm sap-bp-dedupe-matcher

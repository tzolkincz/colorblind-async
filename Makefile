.PHONY: install
install:
	pip3 install -r requirements.txt

.PHONY: test
test:
	python -m pytest tests

.PHONY: install
install:
	pip3 install -r requirements.txt

.PHONY: test
test:
	DEBUG_COLORBLIND_ASYNC=1 python -m pytest tests

.PHONY: install
install:
	pip3 install -r requirements.txt

.PHONY: test
test:
	DEBUG_COLORBLIND_ASYNC=1 python -m pytest tests

.PHONY: build
build:
	- rm dist/*
	python3 -m build

.PHONY: publish
publish:
	python3 -m twine upload --repository pypi dist/*

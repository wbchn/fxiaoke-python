# Make will use bash instead of sh
SHELL := /usr/bin/env bash

ROOT := ${CURDIR}

.PHONY: test
test:
	GCLOUD_PROJECT=$(GCLOUD_PROJECT) python3 setup.py test

.PHONY: clean
clean:
	@rm -fr build dist .eggs *.egg-info
	@rm -fr */__pycache__

.PHONY: package
package:
	@rm -fr build dist .eggs *.egg-info
	python3 setup.py sdist bdist_wheel

.PHONY: dist
dist: clean package
	python3 -m twine check dist/*
	python3 -m twine upload dist/*
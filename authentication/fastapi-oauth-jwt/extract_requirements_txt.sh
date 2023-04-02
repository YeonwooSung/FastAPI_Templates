#!/bin/bash
poetry export -f requirements.txt --without-hashes > requirements.txt

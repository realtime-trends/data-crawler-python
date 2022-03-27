#!/bin/bash

git submodule update --remote
poetry run python main.py
cd data
git add trends.json
git commit -m "update: trends update."
git push origin main
cd ..
git commit -m "update: trends update."
git push origin main -f

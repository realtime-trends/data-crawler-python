#!/bin/bash

git submodule update
poetry run python main.py
cd data
git add trends.json
git commit -m "update: trends update."
git push
cd ..
git commit -m "update: trends update."
git push origin main -f

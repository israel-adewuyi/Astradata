#!/usr/bin/env bash  
set -xeuo pipefail  # This makes the script exit on any error 

div=3

PYTHONUNBUFFERED=1 \
python dataset.py \
    --div=$div \
    2>&1 | tee scraper.log

PYTHONUNBUFFERED=1 \
python codeforces.py \
    --div=$div \
    --dir="datafiles/div$div.csv" \
    2>&1 | tee -a scraper.log

PYTHONUNBUFFERED=1 \
python atcoder.py \
    2>&1 | tee -a scraper.log
#!/usr/bin/env bash
set -o errexit

pip install -r requirements_1.txt
pip install djongo==1.3.6 --no-deps
pip install -r requirements_2.txt
python manage.py collectstatic --no-input
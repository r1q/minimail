#!/bin/sh

. bin/activate
pip install -r requirements.txt
pip install gunicorn
./bin/gunicorn -b 127.0.0.1:9999 minimail.wsgi:application

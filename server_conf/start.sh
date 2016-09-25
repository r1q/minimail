#!/bin/sh

. bin/activate
gunicorn -b 127.0.0.1:9999 minimail.wsgi:application

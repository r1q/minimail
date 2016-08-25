#!/bin/bash

# Replace these three settings.
PROJDIR="/var/www/minimail.fullweb.io"
PIDFILE="$PROJDIR/live_django.pid"

cd $PROJDIR
source ../bin/activate

if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

gunicorn -D -b 127.0.0.1:9999 -p $PIDFILE minimail.wsgi:application

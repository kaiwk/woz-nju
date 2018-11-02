#!/usr/bin/env bash

. venv/bin/activate

while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done

exec gunicorn "app:create_app()" -w 4 -b 0.0.0.0:5000 \
              --log-config ./docker/conf/gunicorn/logging.conf \
              --log-level info \
              --reload

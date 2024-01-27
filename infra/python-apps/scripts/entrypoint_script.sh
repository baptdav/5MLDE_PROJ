#!/bin/bash

sleep 3

cd code
prefect config set PREFECT_API_URL=http://0.0.0.0:4200/api
prefect server database reset -y
prefect config set PREFECT_API_DATABASE_CONNECTION_URL='sqlite+aiosqlite:////root/.prefect/prefect.db'

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
#!/bin/bash

cd /opt/newsroom/

# wait for elastic to be up
printf 'waiting for elastic.'
until $(curl --output /dev/null --silent --fail "${ELASTICSEARCH_URL}"); do
    printf '.'
    sleep .5
done
echo 'done.'

# wait for client 
printf 'waiting for client.'
until $(curl --output /dev/null --silent --fail "${WEBPACK_SERVER_URL}/manifest.json"); do
    printf '.'
    sleep .5
done
echo 'done.'

# app init
python3 manage.py create_user admin@localhost.com admin admin admin true
python3 manage.py elastic_init

if [[ -d dump ]]; then
    echo 'installing demo data'
    mongorestore -h mongo --gzip dump
    python3 manage.py index_from_mongo --all
fi

exec "$@"
#!/bin/bash
# set -e

echo 'starting Newsroom'

# wait for elastic to be up
printf 'waiting for elastic.'
until $(curl --output /dev/null --silent --head --fail "${ELASTICSEARCH_URL}"); do
    printf '.'
    sleep .5
done
echo 'done.'

cd /opt/newsroom/e2e/server/

# app init
python3 manage.py elastic_init

echo "WEBPACK PATH at ${WEBPACK_MANIFEST_PATH}"
ls -l ${WEBPACK_MANIFEST_PATH}

exec "$@"
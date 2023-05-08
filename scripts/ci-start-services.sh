#!/usr/bin/env bash

docker-compose -f docker-compose-services.yml up -d
while ! curl -sfo /dev/null 'http://localhost:9200/'; do echo -n '.' && sleep .5; done

cd e2e
npm run start-client-server &
sleep 2

cd server
honcho start &
cd ../../

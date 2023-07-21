# Setting up newsroom for development

## Repositories

Use `develop` branches of `newsroom-core` and `newsroom-app` repositories.

## Install dependencies

* docker engine - follow instructions at https://docs.docker.com/engine/install/ubuntu
* `sudo apt install docker-compose`
* `sudo apt install git`
* `sudo apt install python3.10-venv` (may vary depending on python version)
* `sudo apt-get install python3-dev`
* `sudo apt install nodejs`
* `sudo apt install npm`
* `sudo npm install -g n`
* use node 14 - `sudo n 14`

## Setup and link newsroom-core client
* navigate to `newsroom-core`
* `npm install`
* `npm link`

## Start client (needs to be started before back-end server)
* navigate to `newsroom-app/client`
* `npm install`
* `npm link newsroom-core`
* `npm start`

## Start server

There are two options, if you only need to develop UI go for A,
otherwise B.

### A) Start server via docker
* navigate to `newsroom-app`
* `docker-compose up server`

#### Updating local server after pulling new code via git
* `docker-compose stop`
* `docker-compose build --no-cache server`

### B) Running the server in dev mode

#### Starting required services via docker (redis, mongo, elastic)
* navigate to `newsroom-app`
* `docker-compose up redis mongo elastic`

#### Create .env file
* navigate to `newsroom-app/server`
* create .env file with the following contents:

```
WEBPACK_ASSETS_URL=http://localhost:8080
WEBPACK_SERVER_URL=http://localhost:8080
SECRET_KEY=newsroom
```

#### Start local server
* navigate to `newsroom-app`
* `cd server`
* create virtual environment `python3 -m venv env`
* activate virtual environment `source env/bin/activate`
* install python dependencies - `pip install -Ur requirements.txt`
* link local server - `pip install -Ue <path-to-newsroom-core>`
* prepare system including elastic `python manage.py initialize_data`
* create a user - `python manage.py create_user admin@example.com admin John Doe true`
* `python manage.py elastic_init`
* start server - `honcho start -p 5050`

#### Updating local server after pulling new code via git

After fetching latest code run the following commands:

* `python manage.py data_upgrade`
* `python manage.py schema_migrate || true `

It will run database migrations when needed.


## Setup Superdesk to publish news items to Newshub

### Create a subscriber

* Go to Superdesk settings -> Subscribers -> Add new
* Set "Target Type" to "All"
* Set "Sequence number settings" to 1 and 10.
* Click "Add new destination"
* Set "Format" to "Newsroom NINJS"
* Set "Delivery type" to "HTTP Push"
* Set "Resource URL" to "http://localhost:5050/push"
* Set "Assets URL" to "http://localhost:5050/push_binary"
* Set "Secret token" to "newsroom"
* Save destination
* Save subscriber






# Terminal 1 - starting the client:
```
cd e2e

npm install
npm run start
```
# Terminal 2 - starting the e2e backend:
```
cd ~/newsroom-core

python3 -m venv env
source env/bin/activate
pip install --upgrade pip wheel setuptools
pip install -e .
cd e2e/server
honcho start -p 5050
```

# Terminal 3 - running the tests:
```
cd e2e
```
```
npm run cypress-ui
```
`or if you want to focus a specific test run the following command:`
```
npm run cypress-ci
```

**Note: You need to start the client before the backend**

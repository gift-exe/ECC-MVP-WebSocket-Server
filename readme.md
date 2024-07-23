## Steps to run the server
---
#### Step 1: Create Virtual Environment:
`$ python -m venv ws-env`

#### Step 2: Acitivate Virtual Environment:
`$ source ws-env/bin/activate`

#### Step 3: Install Requirements.txt
`(ws-env) $ pip install -r requirements.txt`

#### Step 4: Run Server (version 2):
`(ws-env) $ python server_v2.py`

## Endpoints
---
### There are three endpoints on this server:
- `/client`: which is meant for callers (end-users) to connect to and send their conversations with the AI agent
- `/monitor`: this is meant for the monitor user(s) to mmonitor the conversations between users, and the AI agent
- `/history`: this endpoint returns the complete conversation of the caller and the AI agent in a call session

## Testing
---
- To test `/client` endpoint you sould run the `test_message.py` script, which sends a message to the ws server.
- To test the `/monitor` endpoint you can run the `index.html` file, to connect to the ws server as a monitor client.
- To test the `/history` endpoint run the `test_get_history.py` script, to get the message converation history from the test caller.

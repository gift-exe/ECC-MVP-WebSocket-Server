## Steps to run the server
---
#### Step 1: Create Virtual Environment:
`$ python -m venv ws-env`

#### Step 2: Acitivate Virtual Environment:
`$ source ws-env/bin/activate`

#### Step 3: Install Requirements.txt
`(ws-env) $ pip install -r requirements.txt`

#### Step 4: Run Server:
`(ws-env) $ python server.py`

#### After running server connect to server as MONITOR CLIENT with this url: 
`ws://localhost:6789/monitor`

#### To send test messages use the `test.py` script like so:
`(ws-env) $ python test.py`



import asyncio
import websockets
import json


async def get_history():
    uri = 'ws://localhost:6789/history'
    identifier = 'test_client'

    async with websockets.connect(uri) as websocket:
        # Send identifier to the server
        #await websocket.send(identifier)

        # Create a payload
        payload = {
            'client_id':identifier
        }

        # Send the payload to the server
        await websocket.send(json.dumps(payload))

        # Receive acknowledgment from the server
        response = await websocket.recv()
        print(f"Received from server: {json.loads(response)}")

asyncio.run(get_history())
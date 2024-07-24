import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def send_payload():
    uri = f'{os.getenv('WS_URL')}/client'
    identifier = 'test_client'

    async with websockets.connect(uri) as websocket:
        # Send identifier to the server
        await websocket.send(identifier)

        # Create a payload
        payload = {
            'question': 'Hello',
            'answer': 'ECC, What is your Emergency?',
            'from_phone': 123456789,
            'sid': 123
        }

        # Send the payload to the server
        await websocket.send(json.dumps(payload))

        # Receive acknowledgment from the server
        response = await websocket.recv()
        print(f"Received from server: {response}")

# Run the test
asyncio.run(send_payload())
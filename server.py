import asyncio
import websockets
import json

import warnings
warnings.filterwarnings('ignore')

# Dictionary to store connected clients with their identifiers
connected_clients = {}

# Variable to store the monitor client websocket
monitor_client = None

async def conversation_handler(websocket, path):
    global monitor_client

    if path == "/monitor":
        # Register the monitor client
        try:
            monitor_client = websocket
            print('Monitor Client Connected')
            
            async for messages in websocket:
                # Keep connection open
                ...
                
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Monitor Client Disconnected: {e}")

        except Exception as e:
            print('An Error Occured While Connecting Monitor Client')
            raise e
        finally:
            monitor_client = None
    else:
        # Register the regular client
        identifier = await websocket.recv()
        connected_clients[identifier] = websocket

        try:
            async for message in websocket:
                data = json.loads(message)

                # Print the received message
                print(f"{data['from_phone']}: {data['question']} -> {data['answer']}")

                # Send the message to the monitor client if it is connected
                if monitor_client:
                    await monitor_client.send(json.dumps({
                        'from_phone': data['from_phone'],
                        'question': data['question'],
                        'answer': data['answer']
                    }))

                # Send acknowledgment to the client
                await websocket.send(json.dumps({"status": "Message received successfully"}))
        except Exception as e:
            print('An error occured while receiving message from client')
            raise e
        finally:
            # Unregister the client
            if identifier in connected_clients:
                del connected_clients[identifier]

start_server = websockets.serve(conversation_handler, '0.0.0.0', 6789)
print('SERVER STARTED')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


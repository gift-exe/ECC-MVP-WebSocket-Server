import warnings
warnings.filterwarnings('ignore')


import websockets
import asyncio
import json
import aioredis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')


CLIENT_KEY = 'clients'
MONITOR_KEY = 'monitors'
MESSAGE_HISTORY_KEY = 'message_history'


async def get_redis_connection():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)

async def register_client(redis, client_id:str, websocket):
    await redis.hset(CLIENT_KEY, client_id, websocket.remote_address[0])

async def unregister_client(redis, client_id:str):
    await redis.hdel(CLIENT_KEY, client_id)

async def register_monitor(redis, monitor_id:str, websocket):
    await redis.hset(MONITOR_KEY, monitor_id, websocket.remote_address[0])

async def unregister_monitor(redis, monitor_id:str):
    await redis.hdel(MONITOR_KEY, monitor_id)

async def store_message(redis, client_id:str, message_data):
    await redis.rpush(f'{MESSAGE_HISTORY_KEY}:{client_id}', json.dumps(message_data))

async def get_message_history(redis, client_id:str):
    return await redis.lrange(f'{MESSAGE_HISTORY_KEY}:{client_id}', 0, -1)

async def regular_client_handler(websocket):
    redis = await get_redis_connection()
    client_id = await websocket.recv()
    await register_client(redis, client_id, websocket)
    print(f'new client with id: {client_id} -- CONNECTED \n')

    try:
        async for message in websocket:
            message_data = json.loads(message)
            await store_message(redis, client_id, message_data)

            # publish message
            await redis.publish('monitor_channel', json.dumps({
                'client_id':client_id,
                'message':message_data
            }))
            res = {'message':f'payload received from {client_id} successfully'}
            print(res, '\n')
            await websocket.send(json.dumps(res))
            
    except Exception as e:
        res = {'message':f'an error occured with client with id: {client_id} \n', 'error':f'{e}'}
        print(res, '\n')
        await websocket.send(json.dumps(res))
    finally:
        res = {'message':f'client with id: {client_id} -- DISCONNECTED \n'}
        print(res, '\n')
        await websocket.send(json.dumps(res))
        await unregister_client(redis, client_id)
        await redis.close()
        # await redis.wait_closed()

async def monitor_client_handler(websocket):
    redis = await get_redis_connection()
    monitor_id = await websocket.recv()
    await register_monitor(redis, monitor_id, websocket)
    pub = redis.pubsub()
    await pub.subscribe('monitor_channel')
    print(f'new monitor client with id: {monitor_id} -- CONNECTED \n')

    try:
        async for message in pub.listen():
            if message['type'] == 'message':
                await websocket.send(message['data'])
            
    except Exception as e:
        res = {'message':f'an error occured with monitor client with id: {monitor_id} \n', 'error':f'{e}'}
        print(res, '\n')
        await websocket.send(json.dumps(res))
    finally:
        res = {'message':f'monitor client with id: {monitor_id} DISCONNECTED \n'}
        print(res, '\n')
        await websocket.send(json.dumps(res))
        await unregister_client(redis, monitor_id)
        await redis.close()
        # await redis.wait_closed()
        
        

async def message_history_handler(websocket):
    redis = await get_redis_connection()
    try:
        async for message in websocket:
            request_data = json.loads(message)
            client_id = request_data.get('client_id')
            history = await get_message_history(redis, client_id)
            await websocket.send(json.dumps(history))
    except Exception as e:
        raise e
    finally:
        await redis.close()
        await redis.wait_closed()
        
async def handler(websocket, path):
    if path == '/client':
        await regular_client_handler(websocket=websocket)
    elif path == '/monitor':
        await monitor_client_handler(websocket=websocket)
    elif path == '/history':
        await message_history_handler(websocket=websocket)
    else:
        await websocket.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    server = websockets.serve(handler, '0.0.0.0', port)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
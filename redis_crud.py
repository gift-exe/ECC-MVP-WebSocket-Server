import aioredis
import os
from dotenv import load_dotenv
import json

load_dotenv()

CLIENT_KEY = 'clients'
MONITOR_KEY = 'monitors'
MESSAGE_HISTORY_KEY = 'message_history'

REDIS_URL = os.getenv('REDIS_URL')


async def get_redis_connection():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)

async def register_client(redis, client_id:str, phone_number):
    await redis.hset(CLIENT_KEY, client_id, phone_number)

async def unregister_client(redis, client_id:str):
    await redis.hdel(CLIENT_KEY, client_id)

async def register_monitor(redis, monitor_id:str, websocket):
    await redis.hset(MONITOR_KEY, monitor_id, vars(websocket).get('_headers').get('origin'))

async def unregister_monitor(redis, monitor_id:str):
    await redis.hdel(MONITOR_KEY, monitor_id)

async def store_message(redis, client_id:str, message_data):
    await redis.rpush(f'{MESSAGE_HISTORY_KEY}:{client_id}', json.dumps(message_data))

async def store_message_v2(redis, client_id:str, message_data):
    client_exists = await redis.hexists(CLIENT_KEY, client_id)
    if not client_exists:
        # Register the client if it doesn't exist
        await register_client(redis, client_id, message_data['from_phone'])
    await redis.rpush(f'{MESSAGE_HISTORY_KEY}:{client_id}', json.dumps(message_data))
    return True

async def get_message_history(redis, client_id:str):
    return await redis.lrange(f'{MESSAGE_HISTORY_KEY}:{client_id}', 0, -1)
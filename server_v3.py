import warnings
warnings.filterwarnings('ignore')

import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from redis_crud import *
import schema

load_dotenv()

app = FastAPI()

@app.websocket('/client')
async def regular_client_handler(websocket: WebSocket):
    await websocket.accept()
    redis = await get_redis_connection()
    client_id = await websocket.receive_text()
    await register_client(redis, client_id, websocket)
    print(f'new client with id: {client_id} -- CONNECTED \n')

    try:
        while True:
            message = websocket.receive_text()
            message_data = json.loads(message)
            await store_message(redis, client_id, message_data)

            # publish message
            await redis.publish('monitor_channel', json.dumps({
                'client_id':client_id,
                'message':message_data
            }))
            res = {'message':f'payload received from {client_id} successfully'}
            print(res, '\n')
            await websocket.send_text(json.dumps(res))
        
    except WebSocketDisconnect:
        res = {'message': f'client with id: {client_id} -- DISCONNECTED \n'}
        print(res, '\n')
        await unregister_client(redis, client_id)
        await redis.close()

    except Exception as e:
        res = {'message':f'an error occured with client with id: {client_id} \n', 'error':f'{e}'}
        print(res, '\n')
        await websocket.send(json.dumps(res))

@app.post('/send')
async def client_handler_webhook(payload: schema.ClientPayload):
    payload = schema.ClientPayload.to_dict(payload)
    redis = await get_redis_connection()
    client_id = payload['sid']
    await store_message_v2(redis, client_id, payload)
    await redis.publish('monitor_channel', json.dumps({
        'client_id': client_id,
        'message': payload
    }))

    await redis.close()
    return {"status": "message sent"}

@app.websocket('/monitor')
async def monitor_client_handler(websocket: WebSocket):
    await websocket.accept()
    redis = await get_redis_connection()
    monitor_id = await websocket.receive_text()
    await register_monitor(redis, monitor_id, websocket)
    pub = redis.pubsub()
    await pub.subscribe('monitor_channel')
    print(f'new monitor client with id: {monitor_id} -- CONNECTED \n')

    try:
        async for message in pub.listen():
            if message['type'] == 'message':
                data = message['data']
                print(eval(data))
                print(type(eval(data)))
                await websocket.send_text(data) 
    except WebSocketDisconnect:
        res = {'message': f'monitor client with id: {monitor_id} DISCONNECTED \n'}
        print(res, '\n')
        await unregister_monitor(redis, monitor_id)
        await redis.close()
    except Exception as e:
        res = {'message':f'an error occured with monitor client with id: {monitor_id}', 'error': str(e)}
        await websocket.send_text(json.dumps(res))
    
@app.get('/history/{client_id}')
async def message_history_handler(client_id: str):
    redis = await get_redis_connection()
    history = await get_message_history(redis, client_id)
    await redis.close()
    return JSONResponse(content=history)

@app.get('/history/')
async def get_all_calls():
    redis = await get_redis_connection()
    history_raw = await get_call_history(redis)

    print(history_raw.values())
    history = [json.loads(call) for call in history_raw.values()]


    await redis.close()
    return JSONResponse(content=history)


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT'))
    uvicorn.run(app, host='0.0.0.0', port=port)
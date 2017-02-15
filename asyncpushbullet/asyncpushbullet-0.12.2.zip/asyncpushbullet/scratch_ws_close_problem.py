import asyncio
import aiohttp

# Closing the echo.websocket.org connection works as expected
# Closing the stream.pushbullet.com connection hangs

async def run():
    session = aiohttp.ClientSession()
    API_KEY = "RrFnc1xaeQXnRrr2auoGA1e8pQ8MWmMF"
    async with session.ws_connect('wss://stream.pushbullet.com/websocket/' + API_KEY) as ws:
    # async with session.ws_connect("wss://echo.websocket.org") as ws:
        ws.send_json({"hello": "world"})

        async def _timeout():
            await asyncio.sleep(2)
            print('closing ... ', end="", flush=True)
            await ws.close()
            print('... closed. Should see "broke out of ..." messages next')

        asyncio.get_event_loop().create_task(_timeout())

        async for ws_msg in ws:
            print("ws_msg:", ws_msg)

        print("broke out of async for loop")
    print("broke out of async with")
    session.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
print("goodbye")




# loop.create_task(run_websocket_server())
# loop.create_task(run())
# loop.run_forever()



#
#
# async def run_websocket_server():
#     app = web.Application()
#
#     async def _ws_handler(request):
#         ws = web.WebSocketResponse()
#         await ws.prepare(request)
#         counter = 1
#         while not ws.closed:
#             try:
#                 await asyncio.sleep(5)
#             except Exception as e:
#                 print("sleep exception", e)
#                 break
#             ws.send_json({"ping": counter})
#             counter += 1
#         return ws
#
#     app.router.add_get("/", _ws_handler)
#     await app.startup()
#     handler = app.make_handler()
#     srv = await asyncio.get_event_loop().create_server(handler, port=9999)
#

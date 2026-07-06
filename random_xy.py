import asyncio
import json
import random
import websockets

x = 0.5
y = 0.5


async def main():

    global x
    global y

    async with websockets.connect("ws://localhost:8765") as ws:

        while True:

            x += random.uniform(-0.02, 0.02)
            y += random.uniform(-0.02, 0.02)

            x = max(0, min(1, x))
            y = max(0, min(1, y))

            print(x,y)

            await ws.send(json.dumps({
                "type":"producer",
                "x":x,
                "y":y
            }))

            await asyncio.sleep(0.02)  #0.02 or 3


asyncio.run(main())
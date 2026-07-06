import asyncio
import json
import websockets

latest = {
    "x": 0.5,
    "y": 0.5
}

clients = set()


async def handler(ws):
    clients.add(ws)

    try:
        async for message in ws:

            data = json.loads(message)

            # Producer updates x,y
            if data["type"] == "producer":
                latest["x"] = data["x"]
                latest["y"] = data["y"]

                send = json.dumps({
                    "x": latest["x"],
                    "y": latest["y"]
                })

                for c in list(clients):
                    if c != ws:
                        try:
                            await c.send(send)
                        except:
                            pass

    finally:
        clients.remove(ws)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server running")
        await asyncio.Future()


asyncio.run(main())
import asyncio
import json
import math
import websockets
import tobii_research as tr
import time

clients = set()
loop = None


async def handler(ws):
    clients.add(ws)
    print("Website connected")

    try:
        await ws.wait_closed()
    finally:
        clients.remove(ws)
        print("Website disconnected")


async def broadcast(x, y):
    if not clients:
        return

    msg = json.dumps({
        "x": x,
        "y": y,
    })

    dead = []

    for client in clients:
        try:
            await client.send(msg)
        except:
            dead.append(client)

    for client in dead:
        clients.discard(client)


def gaze_data_callback(gaze_data):
    global loop

    left_x, left_y = gaze_data["left_gaze_point_on_display_area"]
    right_x, right_y = gaze_data["right_gaze_point_on_display_area"]

    if math.isnan(left_x) or math.isnan(right_x):
        x = -1
        y = -1
    else:
        x = (left_x + right_x) / 2
        y = (left_y + right_y) / 2

    unix_ms = time.time() * 1000

    print(f"x={x:.6f}, y={y:.6f}, unix={unix_ms:.6f}")

    asyncio.run_coroutine_threadsafe(
        broadcast(x, y),
        loop
    )


async def main():
    global loop

    loop = asyncio.get_running_loop()

    # Find eye tracker
    eyetrackers = tr.find_all_eyetrackers()
    if not eyetrackers:
        print("No Tobii found.")
        return

    eyetracker = eyetrackers[0]

    print("Connected to:", eyetracker.device_name)

    # Subscribe to Tobii
    eyetracker.subscribe_to(
        tr.EYETRACKER_GAZE_DATA,
        gaze_data_callback,
        as_dictionary=True,
    )

    print("Streaming gaze...")
    print("WebSocket server: ws://localhost:8765")

    try:
        async with websockets.serve(handler, "localhost", 8765):
            await asyncio.Future()  # run forever
    finally:
        eyetracker.unsubscribe_from(
            tr.EYETRACKER_GAZE_DATA,
            gaze_data_callback,
        )


if __name__ == "__main__":
    asyncio.run(main())
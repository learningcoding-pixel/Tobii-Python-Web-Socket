import asyncio
import json
import math
import sys
import websockets
import tobii_research as tr
import time

loop = None
ws = None
found_eyetrackers = tr.find_all_eyetrackers()

if not found_eyetrackers:
    print("No Tobii eye tracker found.")
    sys.exit(1)

my_eyetracker = found_eyetrackers[0]

print("Address:", my_eyetracker.address)
print("Model:", my_eyetracker.model)
print("Serial:", my_eyetracker.serial_number)

async def send_gaze(x, y):
    global ws

    if ws is None:
        return

    await ws.send(json.dumps({
        "type": "producer",
        "x": x,
        "y": y,
    }))


def gaze_data_callback(gaze_data):
    global loop

    left_x, left_y = gaze_data["left_gaze_point_on_display_area"]
    right_x, right_y = gaze_data["right_gaze_point_on_display_area"]

    x = (left_x + right_x) / 2
    y = (left_y + right_y) / 2

    if math.isnan(x) or math.isnan(y):
        x = -1
        y = -1

    unix_time = time.time()
    
    print(f"x={x:.6f}, y={y:.6f}, unix={unix_time:.6f}")

    asyncio.run_coroutine_threadsafe(
        send_gaze(x, y),
        loop
    )


async def main():
    global loop, ws

    loop = asyncio.get_running_loop()

    ws = await websockets.connect("ws://localhost:8765")
    print(type(my_eyetracker))
    print(repr(my_eyetracker))

    my_eyetracker.subscribe_to(
        tr.EYETRACKER_GAZE_DATA,
        gaze_data_callback,
        as_dictionary=True,
    )

    print("Streaming gaze...")

    await asyncio.Future()      # keep program alive


asyncio.run(main())
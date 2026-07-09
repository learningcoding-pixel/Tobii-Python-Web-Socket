import asyncio
import json
import time
import websockets
import tobii_research as tr
import sys
import math

# Latest gaze position
x = 0.5
y = 0.5

print("Subscribing...")
print(tr.__version__)
print(sys.executable)

# Find eye tracker
found_eyetrackers = tr.find_all_eyetrackers()

if not found_eyetrackers:
    print("No Tobii eye tracker found.")
    sys.exit(1)

my_eyetracker = found_eyetrackers[0]

print("Address:", my_eyetracker.address)
print("Model:", my_eyetracker.model)
print("Name:", my_eyetracker.device_name)
print("Serial number:", my_eyetracker.serial_number)

# Sampling frequency
print("Current frequency:", my_eyetracker.get_gaze_output_frequency())
print("Available frequencies:", my_eyetracker.get_all_gaze_output_frequencies())


def gaze_data_callback(gaze_data):
    global x, y

    left_x, left_y = gaze_data["left_gaze_point_on_display_area"]
    right_x, right_y = gaze_data["right_gaze_point_on_display_area"]

    # Average left and right eye gaze
    x = (left_x + right_x) / 2
    y = (left_y + right_y) / 2


async def main():
    global x, y

    # Subscribe to gaze data
    my_eyetracker.subscribe_to(
        tr.EYETRACKER_GAZE_DATA,
        gaze_data_callback,
        as_dictionary=True,
    )

    print("Subscribed!")

    last_print = time.time()

    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            print("Connected to WebSocket server.")

            while True:
                

                #if math.isnan(x) or math.isnan(y):
                #    x = -1
                #    y = -1
                
                #print(f"Alive... x={repr(x)}, y={repr(y)}")


                # Send latest gaze coordinates
                if not (math.isnan(x) or math.isnan(y)):
                    await ws.send(
                        json.dumps(
                            {
                                "type": "producer",
                                "x": x,
                                "y": y,
                                }
                                )
                                )
                    print(f"Sent gaze coordinates: x={x}, y={y}")
                else:
                    await ws.send(
                        json.dumps(
                            {
                                "type": "producer",
                                "x": -1,
                                "y": -1,
                            }
                        )
                    )
                    print("Sent invalid gaze coordinates.")

                # 50 Hz update rate
                #await asyncio.sleep(0.0083) #0.02

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        my_eyetracker.unsubscribe_from(
            tr.EYETRACKER_GAZE_DATA,
            gaze_data_callback,
        )
        print("Unsubscribed from eye tracker.")


if __name__ == "__main__":
    asyncio.run(main())
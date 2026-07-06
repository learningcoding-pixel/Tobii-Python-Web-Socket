import tobii_research as tr
import sys
import time

print("Subscribing...")
#https://developer.tobiipro.com/python/python-step-by-step-guide.html
print(tr.__version__)
print(sys.executable)


found_eyetrackers = tr.find_all_eyetrackers()

my_eyetracker = found_eyetrackers[0]
print("Address: " + my_eyetracker.address)
print("Model: " + my_eyetracker.model)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
print("Serial number: " + my_eyetracker.serial_number)


def gaze_data_callback(gaze_data):
    left_x, left_y = gaze_data["left_gaze_point_on_display_area"]
    right_x, right_y = gaze_data["right_gaze_point_on_display_area"]

    x = (left_x + right_x) / 2
    y = (left_y + right_y) / 2

    print(f"x={x:.4f}, y={y:.4f}")

my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)


print("Subscribed!")

while True:
    print("Alive...")
    time.sleep(2)

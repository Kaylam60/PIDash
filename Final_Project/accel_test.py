import smbus2
import time
import subprocess
import os
import threading
from datetime import datetime

# i2c configuration
i2c_bus = 1
device_address = 0x18

bus = smbus2.SMBus(i2c_bus)


# Stream URLs for front and rear cameras
front_stream_url = "http://10.49.99.246:8888/camera1/index.m3u8"
rear_stream_url = "http://10.49.99.246:8888/camera2/index.m3u8"


# Directories to save videos
front_save_directory = "/media/pi/BekFast/Pidash/front_camera/"
rear_save_directory = "/media/pi/BekFast/Pidash/rear_camera/"
crash_directory = "/media/pi/BekFast/Pidash/crash_videos/"

# Segment duration (1 minute in seconds)
segment_duration = 60  # Save every minute

# Ensure directories exist
os.makedirs(front_save_directory, exist_ok=True)
os.makedirs(rear_save_directory, exist_ok=True)
os.makedirs(crash_directory, exist_ok=True)

# lis3dh registers
ctrl_reg1 = 0x20
ctrl_reg4 = 0x23
out_x_l = 0x28
out_x_h = 0x29
out_y_l = 0x2a
out_y_h = 0x2b
out_z_l = 0x2c
out_z_h = 0x2d

# configure lis3dh
bus.write_byte_data(device_address, ctrl_reg1, 0x57)  # enable all axes, odr = 100hz
bus.write_byte_data(device_address, ctrl_reg4, 0x80)  # ±2g, continuous update, bdu = 1

# two's complement conversion
def twos_complement(value, bits):
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value

# read accelerometer data
def read_accelerometer():
    x = twos_complement((bus.read_byte_data(device_address, out_x_h) << 8) |
                        bus.read_byte_data(device_address, out_x_l), 16)
    y = twos_complement((bus.read_byte_data(device_address, out_y_h) << 8) |
                        bus.read_byte_data(device_address, out_y_l), 16)
    z = twos_complement((bus.read_byte_data(device_address, out_z_h) << 8) |
                        bus.read_byte_data(device_address, out_z_l), 16)
    return x, y, z

# offsets (calibrate these while stationary)
x_offset = 0
y_offset = 0
z_offset = 0

# gravitational constant
g_constant = 9.80665  # m/s^2

# sensitivity (still in g)
sensitivity = 0.001  # ±2g mode

# high-pass filter for gravity removal
alpha = 0.8  # smoothing factor for filtering gravity
gravity_x, gravity_y, gravity_z = 0, 0, 0  # initialize gravity components

def filter_gravity(x, y, z):
    global gravity_x, gravity_y, gravity_z
    gravity_x = alpha * gravity_x + (1 - alpha) * x
    gravity_y = alpha * gravity_y + (1 - alpha) * y
    gravity_z = alpha * gravity_z + (1 - alpha) * z

    x_linear = x - gravity_x
    y_linear = y - gravity_y
    z_linear = z - gravity_z

    return x_linear, y_linear, z_linear

# low-pass filter for noise reduction
beta = 0.2  # smoothing factor for noise reduction
filtered_x, filtered_y, filtered_z = 0, 0, 0  # initialize filtered components

def low_pass_filter(x, y, z):
    global filtered_x, filtered_y, filtered_z
    filtered_x = beta * x + (1 - beta) * filtered_x
    filtered_y = beta * y + (1 - beta) * filtered_y
    filtered_z = beta * z + (1 - beta) * filtered_z

    return filtered_x, filtered_y, filtered_z

# threshold for hard stop detection
hard_stop_threshold = -1.0
crash_detected=False
try:
    while True:
        x_raw, y_raw, z_raw = read_accelerometer()
        # apply offsets
        x = (x_raw - x_offset) * sensitivity * g_constant
        y = (y_raw - y_offset) * sensitivity * g_constant
        z = (z_raw - z_offset) * sensitivity * g_constant

        # apply gravity filter
        x_linear, y_linear, z_linear = filter_gravity(x, y, z)

        # apply low-pass filter
        x_stable, y_stable, z_stable = low_pass_filter(x_linear, y_linear, z_linear)

        # detect hard stop in m/s²
        deceleration = -x_stable  # assuming forward/backward is along the x-axis
        if deceleration > hard_stop_threshold:
            print(f"hard stop detected! x: {x_stable:.2f} m/s²")
            crash_detected= True
            time.sleep(10)
            
        print(f"x: {x_stable:.2f} m/s², y: {y_stable:.2f} m/s², z: {z_stable:.2f} m/s²")
        time.sleep(0.1)  # 10hz loop
        
except KeyboardInterrupt:
    print("stopped by user.")
    bus.close()
    
def save_video_stream(stream_url, save_directory, camera_name):
    """
    Saves a video stream to a specified directory in 1-minute segments.
    Moves the current file to crash directory if a crash is detected.
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    while True:
        # Generate filename based on current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(save_directory, f"{camera_name}_{timestamp}.mp4")

        # FFmpeg command to save stream
        ffmpeg_command = [
            "ffmpeg",
            "-i", stream_url,
            "-t", str(segment_duration),
            "-c", "copy",
            output_file
        ]

        print(f"Saving {camera_name} video to {output_file}")
        try:
            subprocess.run(ffmpeg_command, check=True)
            
            # If crash detected, move the current file to crash directory
            if crash_detected.is_set():
                crash_detected.clear()
                crash_file = os.path.join(crash_directory, f"{camera_name}_CRASH_{timestamp}.mp4")
                os.rename(output_file, crash_file)
                print(f"{camera_name} crash video saved to {crash_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error while saving {camera_name} video: {e}")
            continue

if __name__ == "__main__":
    # Start saving streams in separate threads
    front_thread = threading.Thread(target=save_video_stream, args=(front_stream_url, front_save_directory, "front"))
    rear_thread = threading.Thread(target=save_video_stream, args=(rear_stream_url, rear_save_directory, "rear"))

    front_thread.start()
    rear_thread.start()

    # Wait for threads to complete
    front_thread.join()
    rear_thread.join()
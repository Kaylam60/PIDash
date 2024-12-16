import subprocess
import os
import threading
import time
from datetime import datetime
import smbus2  # For I2C communication with LIS3DH
import RPi.GPIO as GPIO
import glob
#GPIO.setmode(GPIO.BCM)

#GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Stream URLs for front and rear cameras
front_stream_url = "http://192.168.135.98:8888/camera1/index.m3u8"
rear_stream_url  = "http://192.168.135.98:8888/camera2/index.m3u8"


# Directories to save videos
front_save_directory = "/media/pi/PIDASH/front_camera/"
rear_save_directory = "/media/pi/PIDASH/rear_camera/"
crash_directory = "/media/pi/PIDASH/crash_videos/"

# Segment duration (1 minute in seconds)
segment_duration = 15  # Save every minute

# Accelerometer I2C setup
I2C_BUS = 1
LIS3DH_ADDRESS = 0x18  # Default I2C address for LIS3DH
THRESHOLD = -10  # Crash detection threshold (m/s²)

bus = smbus2.SMBus(I2C_BUS)
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
bus.write_byte_data(LIS3DH_ADDRESS, ctrl_reg1, 0x57)  # enable all axes, odr = 100hz
bus.write_byte_data(LIS3DH_ADDRESS, ctrl_reg4, 0x80)  # ±2g, continuous update, bdu = 1

# Ensure directories exist
os.makedirs(front_save_directory, exist_ok=True)
os.makedirs(rear_save_directory, exist_ok=True)
os.makedirs(crash_directory, exist_ok=True)


button = True

# Function to read accelerometer data
def read_acceleration():
    #bus = smbus.SMBus(I2C_BUS)
    def read_axis(addr):
        low = bus.read_byte_data(LIS3DH_ADDRESS, addr)
        high = bus.read_byte_data(LIS3DH_ADDRESS, addr + 1)
        value = (high << 8) | low
        if value & 0x8000:  # Negative values
            value -= 1 << 16
        return value / 16384.0  # Scale to g-force
    x = read_axis(0x28)
    y = read_axis(0x2A)
    z = read_axis(0x2C)
    return (x, y, z)

# Crash detection flag
crash_detected = threading.Event()

def crash_detection():
    """
    Continuously monitors the accelerometer for crash events.
    """
    while True:
        try:
            x, y, z = read_acceleration()
            total_acceleration = (x**2 + y**2 + z**2)**0.5
            if total_acceleration < THRESHOLD:
                print(f"Crash detected! Acceleration: {total_acceleration} m/s²")
                crash_detected.set()  # Signal a crash
                time.sleep(1)  # Avoid immediate re-triggering
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
        time.sleep(0.1)


def cleanup_old_files(directory, retention_minutes=10):
    """
    Deletes files older than the retention period in minutes.
    """
    now = time.time()
    for file in glob.glob(os.path.join(directory, "*.mp4")):
        if os.path.getmtime(file) < now - (retention_minutes * 60):
            os.remove(file)
            print(f"Deleted old file: {file}")

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
        cleanup_old_files(save_directory, retention_minutes=10)


if __name__ == "__main__":
    # Start crash detection thread
    crash_thread = threading.Thread(target=crash_detection)
    crash_thread.daemon = True
    crash_thread.start()

    # Start saving streams in separate threads
    front_thread = threading.Thread(target=save_video_stream, args=(front_stream_url, front_save_directory, "front"))
    rear_thread = threading.Thread(target=save_video_stream, args=(rear_stream_url, rear_save_directory, "rear"))

    front_thread.start()
    rear_thread.start()

    # Wait for threads to complete
    front_thread.join()
    rear_thread.join()
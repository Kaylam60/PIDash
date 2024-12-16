import subprocess
import os
from datetime import datetime
import threading

# Stream URLs for front and rear cameras
front_stream_url = "http://192.168.135.98:8888/camera1/index.m3u8"
rear_stream_url  = "http://192.168.135.98:8888/camera2/index.m3u8"

# Directories to save videos
front_save_directory = "/media/pi/PIDASH/front_camera/"
rear_save_directory = "/media/pi/PIDASH/rear_camera/"

# Segment duration (1 minute in seconds)
segment_duration = 60  # Save every minute

def save_video_stream(stream_url, save_directory, camera_name):
    """
    Saves a video stream to a specified directory in 1-minute segments.
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    while True:
        # Generate filename based on current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(save_directory, f"{camera_name}_{timestamp}.mp4")

        # FFmpeg command to save stream in 1-minute chunks
        ffmpeg_command = [
            "ffmpeg",
            "-i", stream_url,          # Input stream URL
            "-t", str(segment_duration),  # Save duration (1 minute)
            "-c", "copy",              # No re-encoding
            output_file
        ]

        print(f"Saving {camera_name} video to {output_file}")
        try:
            # Run FFmpeg command
            subprocess.run(ffmpeg_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error while saving {camera_name} video: {e}")
            continue  # Retry next segment

if __name__ == "__main__":
    # Start saving streams in separate threads
    front_thread = threading.Thread(target=save_video_stream, args=(front_stream_url, front_save_directory, "front"))
    rear_thread = threading.Thread(target=save_video_stream, args=(rear_stream_url, rear_save_directory, "rear"))

    front_thread.start()
    rear_thread.start()

    # Wait for both threads to complete
    front_thread.join()
    rear_thread.join()

#!/bin/bash

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed. Please install it first."
    exit 1
fi

# Start streaming from Camera 2
echo "Starting stream from Camera 2..."
ffmpeg -f v4l2 -i /dev/video1 -c:v libx264 -preset ultrafast -tune zerolatency -f rtsp rtsp://localhost:8554/camera2

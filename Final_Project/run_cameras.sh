#!/bin/bash

# Run camera1.py for the first camera in the background
python3 camera1.py &

# Run camera2.py for the second camera in the background
python3 camera2.py &

# Wait for both scripts to complete (if they have termination logic)
wait

echo "Both camera feeds have stopped."

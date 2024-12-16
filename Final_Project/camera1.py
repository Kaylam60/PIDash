import cv2

# Initialize the first camera
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not access camera 0.")
    exit()

# Set resolution (optional)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cam.set(cv2.CAP_PROP_FPS, 30)

while True:
    # Capture a frame
    ret, frame = cam.read()
    if not ret:
        print("Error: Could not read frame from camera 0.")
        break

    # Display the frame
    cv2.imshow('Camera 1 Feed', frame)

    # Save an image and exit when any key is pressed
    key = cv2.waitKey(1)
    if key != -1:
        cv2.imwrite('/home/pi/testimage_cam1.jpg', frame)
        print("Image from Camera 1 saved.")
        break

cam.release()
cv2.destroyAllWindows()
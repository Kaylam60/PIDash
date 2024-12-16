import cv2
cam = cv2.VideoCapture(2)
if not cam.isOpened():
    print("Error: Could not access camera 2.")
    exit()

# Set resolution (optional)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cam.set(cv2.CAP_PROP_FPS, 30)
while True:
    # Capture a frame
    ret, frame = cam.read()
    if not ret:
        print("Error: Could not read frame from camera 2.")
        break

    # Display the frame
    cv2.imshow('Camera 2 Feed', frame)

    # Save an image and exit when any key is pressed
    key = cv2.waitKey(1)
    if key != -1:
        cv2.imwrite('/home/pi/testimage_cam2.jpg', frame)
        print("Image from Camera 2 saved.")
        break

cam.release()
cv2.destroyAllWindows()
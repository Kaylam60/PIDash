# PIDash
A repository containing all the necessary files to run the PIDash implementation on the Raspberry Pi 4

## Setting Up MediaMTX for This Project

This project uses **MediaMTX** (formerly RTSP Simple Server) as the streaming server for real-time video transmission. Follow the steps below to install and configure MediaMTX.

---

### Step 1: Download MediaMTX
1. Visit the [official MediaMTX releases page on GitHub](https://github.com/bluenviron/mediamtx/releases).
2. Download the appropriate binary for your operating system:
   - **Windows**: `mediamtx_windows_amd64.exe`
   - **Linux**: `mediamtx_linux_amd64`
   - **macOS**: `mediamtx_macos_amd64`

---

### Step 2: Install MediaMTX
1. Extract the downloaded file (if it’s in a compressed format like `.zip`).
2. Move the binary to a directory that is accessible via your terminal or command prompt.
   - For Linux/macOS: Add execute permissions by running:
     ```bash
     chmod +x mediamtx_linux_amd64
     ```

---

### Step 3: Configure MediaMTX
1. Create a `mediamtx.yml` configuration file in the same directory as the binary.
2. Use the default configuration or modify it to match your project's requirements:
   - **HLS Protocol Example**:
     ```yaml
     server:
       protocols: [hls, rtsp]
     paths:
       all:
         source: publisher
     ```

---

### Step 4: Run MediaMTX
1. Start the MediaMTX server by executing the binary:
   - For **Windows**:
     ```cmd
     mediamtx_windows_amd64.exe
     ```
   - For **Linux/macOS**:
     ```bash
     ./mediamtx_linux_amd64
     ```
2. The server will start and output logs in the terminal.

---

### Step 5: Integrate with the Project
1. Ensure that the Raspberry Pi camera feed is streaming to the **MediaMTX server** using a supported protocol (e.g., `RTSP` or `HLS`).
2. Access the stream using the server's IP address and port:
   - For **HLS**:
     ```
     http://<server-ip>:8888/live/index.m3u8
     ```
   - For **RTSP**:
     ```
     rtsp://<server-ip>:8554/live
     ```

---

### Optional: Troubleshooting
- If you encounter issues, refer to the [MediaMTX documentation](https://github.com/bluenviron/mediamtx) for additional help.

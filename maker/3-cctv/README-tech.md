https://www.raspberrypi.com/products/raspberry-pi-4-model-b/specifications/

Broadcom BCM2711, H264 1080p30, MPEG-TS, Sony IMX708

4 Mbps = 500 KB/s, 5 MB/chunk, 43 GB/day
shit SD max: 3,000 cycles, 2 MB/s

3321 port

# encryption

deno

AES-GCM or AES-CTR

RSA-OAEP



# aes benchmark

CPUINFO: OPENSSL_armcap=0x81
The 'numbers' are in 1000s of bytes per second processed.
type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
AES-256-CBC      11967.90k    22082.52k    18706.35k    13478.57k    23582.04k    18251.78k

# old

## mp4

libcamera-vid -t 0 --codec yuv420 --width 1920 --height 1080 --framerate 30 --inline --output - | \
TZ=UTC ffmpeg -f rawvideo -pix_fmt yuv420p -s 1920x1080 -i - \
  -c:v h264_v4l2m2m -g 300 -keyint_min 300 -sc_threshold 0 -b:v 4M \
  -f segment -segment_time 10 -reset_timestamps 1 \
  -segment_format mp4 -strftime 1 \
  -movflags frag_keyframe+empty_moov \
  "video_%Y-%m-%d_%H-%M-%S_utc.mp4"

## device detect

v4l2-ctl --list-devices
v4l2-ctl --list-formats-out -d /dev/video11
v4l2-ctl --device=/dev/video11 --all

## gstreamer

gst-inspect-1.0 v4l2h264enc

gst-launch-1.0 -e \
    libcamerasrc !                                   \
        video/x-raw,width=1920,height=1080,framerate=30/1,format=NV12 ! \
    v4l2h264enc output-io-mode=4                     \
        extra-controls="controls,                  \
                       video_bitrate=10000000,     \
                       video_bitrate_mode=0,       \
                       repeat_sequence_header=1,   \
                       h264_profile=4,             \
                       h264_level=11"              \
    ! h264parse                                     \
    ! mp4mux faststart=true                         \
    ! filesink location=cam_1080p30.mp4

gst-launch-1.0 -e \
  libcamerasrc  \
    ! video/x-raw,width=1920,height=1080,framerate=30/1,format=NV12 \
    ! v4l2h264enc output-io-mode=3           \
        extra-controls="controls,repeat_sequence_header=1,video_bitrate=10000000" \
    ! h264parse                              \
    ! mp4mux faststart=true                  \
    ! filesink location=cam_1080p30.mp4

sudo apt install \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libcamera \
    gstreamer1.0-libav \
    gstreamer1.0-plugins-bad \
    gir1.2-gst-plugins-base-1.0 \
    gir1.2-gstreamer-1.0 \
    python3-gi \
    python3-gi-cairo \
    python3-gst-1.0

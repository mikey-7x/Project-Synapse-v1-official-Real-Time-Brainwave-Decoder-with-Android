#!/data/data/com.termux/files/usr/bin/bash

# Start PulseAudio
pulseaudio --start --exit-idle-time=-1

# Set Display
export DISPLAY=:0

# Start Termux-X11
termux-x11 :0 &

# Wait for X11 to be ready
sleep 3

# Start your linux (in my case it is U-Droid's ubuntu) with XFCE4 and execute commands inside it
udroid login jammy:xfce4 << 'EOF'
su - yogesh -c 'export PULSE_SERVER=tcp:127.0.0.1:4713; export DISPLAY=:0; dbus-launch --exit-with-session startxfce4'
EOF


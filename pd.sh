#!/data/data/com.termux/files/usr/bin/bash

# Kill open X11 processes if any
kill -9 $(pgrep -f "termux.x11") 2>/dev/null

# Enable PulseAudio over network
pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1" >/dev/null 2>&1

# Prepare Termux-X11 session
export XDG_RUNTIME_DIR=${TMPDIR}
termux-x11 :0 >/dev/null &

# Wait a few seconds for Termux-X11 to start
sleep 3

# Launch Termux-X11 Android activity
am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1
sleep 1

# Start Ubuntu (i'm installed via MaheshTechnicals script)
# This assumes you're inside the Termux home directory and have startubuntu.sh ready
# Set DISPLAY and PULSE environment variables and run XFCE inside Ubuntu
ubuntu <<'EOL'
export DISPLAY=:0
export PULSE_SERVER=127.0.0.1
dbus-launch --exit-with-session startxfce4
EOL

exit 0

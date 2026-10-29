#!/data/data/com.termux/files/usr/bin/bash

# Kill existing Termux-X11 and PulseAudio instances
pkill -f "termux.x11" 2>/dev/null
pkill pulseaudio 2>/dev/null

# Start PulseAudio with TCP enabled for localhost access
pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1

# Export X11 display environment and runtime dir
export DISPLAY=:0
export XDG_RUNTIME_DIR=/data/data/com.termux/files/usr/tmp

# Start Termux-X11 display
termux-x11 :0 >/dev/null 2>&1 &

# Give X11 time to initialize
sleep 3

# Start Termux-X11 Android activity
am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1
sleep 1

# Start Ubuntu in PRoot with shared tmp and launch XFCE4
proot-distro login ubuntu --shared-tmp -- /bin/bash -c '
  export DISPLAY=:0
  export PULSE_SERVER=127.0.0.1
  export XDG_RUNTIME_DIR=/tmp
  dbus-launch --exit-with-session startxfce4
' 2>&1 | tee ~/xfce4_log.txt
exit 0

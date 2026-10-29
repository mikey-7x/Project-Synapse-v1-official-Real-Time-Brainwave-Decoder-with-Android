#!/data/data/com.termux/files/usr/bin/bash

echo "[*] Resetting audio..."
pulseaudio -k 2>/dev/null
pkill -9 pulseaudio 2>/dev/null
rm -rf ~/.run ~/.config/pulse ~/.pulse-cookie

mkdir -p ~/.config/pulse
cat > ~/.config/pulse/default.pa <<'EOF'
load-module module-native-protocol-unix
load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1
load-module module-aaudio-sink
load-module module-null-sink sink_name=android_sink
set-default-sink android_sink
EOF

export XDG_RUNTIME_DIR=$HOME/.run
mkdir -p $XDG_RUNTIME_DIR/pulse
chmod 700 $XDG_RUNTIME_DIR
chmod 700 $XDG_RUNTIME_DIR/pulse

echo "[*] Starting PulseAudio..."
pulseaudio --daemonize=yes --exit-idle-time=-1

sleep 2

pactl load-module module-loopback source=android_sink.monitor sink=AAudio_sink >/dev/null 2>&1

echo "[*] Starting X11..."
pkill -9 termux-x11 Xorg Xwayland 2>/dev/null
rm -rf $PREFIX/tmp/.X11-unix
mkdir -p $PREFIX/tmp/.X11-unix
chmod 777 $PREFIX/tmp/.X11-unix

termux-x11 :0 &
sleep 2

echo "[*] Launching Void..."
proot-distro login void --shared-tmp -- env DISPLAY=:0 PULSE_SERVER=127.0.0.1 XDG_RUNTIME_DIR=/tmp bash -c '
export PULSE_SERVER=127.0.0.1
export DISPLAY=:0

mkdir -p ~/.asoundrc >/dev/null 2>&1

cat > ~/.asoundrc <<EOF
pcm.!default { type pulse }
ctl.!default { type pulse }
EOF

startxfce4
'

#!/data/data/com.termux/files/usr/bin/bash
# =========================================================================
# Project   : mikey-7x/Termux-projects — Deep Termux & Arch PRoot Cleaner
# Script    : rom_cleaner_termux.sh
# Author    : mikey-7x (https://github.com/mikey-7x)
# Purpose   : Safely reclaims gigabytes of ROM inside Termux and Arch Linux
#             (mpd / proot-distro) without deleting active Wine engines,
#             active Wine prefixes, or user projects.
# Execution : Run directly inside Termux:
#             bash rom_cleaner_termux.sh
# =========================================================================

echo "==========================================================";
echo "  Termux & Arch Linux Deep Storage Cleaner — by mikey-7x  ";
echo "==========================================================";

echo "[*] Storage BEFORE cleanup:";
df -h "$PREFIX";

echo "[1/6] Cleaning Termux host APT package cache...";
apt clean >/dev/null 2>&1 || true;
rm -rf "$PREFIX/var/cache/apt/archives/"* 2>/dev/null;
rm -rf "$HOME/.cache/"* 2>/dev/null;

# Detect Arch Linux rootfs (supports both mpd and proot-distro layouts)
ARCH_MPD="$PREFIX/var/lib/mpd/archlinux";
ARCH_PD="$PREFIX/var/lib/proot-distro/installed-rootfs/archlinux";

for ARCH in "$ARCH_MPD" "$ARCH_PD"; do
  [ -d "$ARCH" ] || continue;
  echo "[*] Found Arch Linux rootfs at: $ARCH";

  echo "[2/6] Cleaning Arch Pacman downloaded package cache (/var/cache/pacman/pkg)...";
  rm -rf "$ARCH/var/cache/pacman/pkg/"* 2>/dev/null;

  echo "[3/6] Removing hidden .backup-* Wine prefixes (active prefixes kept untouched)...";
  rm -rf "$ARCH"/home/*/.xs-7-prefixes/.backup-* 2>/dev/null;
  rm -rf "$ARCH"/root/.xs-7-prefixes/.backup-* 2>/dev/null;

  echo "[4/6] Cleaning Wine Temp folders, xs-7 run logs & browser/yay caches...";
  rm -rf "$ARCH"/home/*/.xs-7-prefixes/*/drive_c/users/*/Temp/* 2>/dev/null;
  rm -rf "$ARCH"/home/*/.xs-7-prefixes/*/drive_c/windows/temp/* 2>/dev/null;
  rm -rf "$ARCH"/root/.xs-7-prefixes/*/drive_c/users/*/Temp/* 2>/dev/null;
  rm -rf "$ARCH"/root/.xs-7-prefixes/*/drive_c/windows/temp/* 2>/dev/null;

  rm -f "$ARCH"/home/*/.config/xs-7/run-*.log 2>/dev/null;
  rm -f "$ARCH"/home/*/.config/xs-7/prefix-*.log 2>/dev/null;
  rm -f "$ARCH"/home/*/.config/xs-7/*.xfce-state.log 2>/dev/null;
  rm -f "$ARCH"/root/.config/xs-7/run-*.log 2>/dev/null;
  rm -f "$ARCH"/root/.config/xs-7/prefix-*.log 2>/dev/null;

  rm -rf "$ARCH"/opt/xs-7/box64/build 2>/dev/null;
  rm -rf "$ARCH"/tmp/yay "$ARCH"/tmp/bubblewrap "$ARCH"/tmp/*.tar* "$ARCH"/tmp/*.zip 2>/dev/null;
  rm -rf "$ARCH"/home/*/.cache/* "$ARCH"/root/.cache/* 2>/dev/null;

  echo "[5/6] Cleaning Arduino CLI/IDE staging installer archives (installed boards kept)...";
  rm -rf "$ARCH"/home/*/.arduino15/staging/* 2>/dev/null;
  rm -rf "$ARCH"/home/*/*/.arduino-data/staging/* 2>/dev/null;
done;

echo "[6/6] Cleaning Android File Manager Recycler trash on /sdcard...";
rm -rf /storage/emulated/0/.FileManagerRecycler/* 2>/dev/null;

echo "";
echo "[*] Storage AFTER cleanup:";
df -h "$PREFIX";
echo "==========================================================";
echo "[*] Cleanup complete! All active engines, prefixes & tools preserved.";

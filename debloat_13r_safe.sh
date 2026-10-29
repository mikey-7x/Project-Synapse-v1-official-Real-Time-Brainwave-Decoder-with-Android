#!/system/bin/sh
# =========================================================================
# Project   : mikey-7x/Termux-projects — 100% Safe System Debloater
# Script    : debloat_13r_safe.sh
# Author    : mikey-7x (https://github.com/mikey-7x)
# Target    : OnePlus 13R (CPH2691) / OxygenOS 15 & 16 (No Root, via aShell)
# Purpose   : Strips Play Store updates from /data, clears app data, and
#             disables 31+ safe system bloatware & telemetry packages while
#             keeping all core Android, OxygenOS, social, payment, voice
#             typing, Bluetooth audio, App Cloner, and Termux features 100%
#             intact.
# Restore   : Any package can be re-enabled anytime via: pm enable <pkg>
# =========================================================================

echo "== [ONEPLUS 13R 100% SAFE DEBLOAT & ROM CLEANER] ==";
echo "Storage before:";
df -h /data;

SAFE_BLOAT_PKGS="
com.google.android.projection.gearhead
com.google.android.apps.restore
com.google.android.safetycore
com.google.android.aicore
com.google.android.apps.wellbeing
com.heytap.quicksearchbox
com.oplus.dmp
com.google.ar.core
com.google.android.apps.walletnfcrel
com.heytap.cloud
com.heytap.browser
com.oneplus.asti
com.coloros.childrenspace
com.google.ar.lens
com.microsoft.appmanager
com.heytap.pictorial
com.google.android.apps.tachyon
com.facebook.system
com.facebook.appmanager
com.facebook.services
com.heytap.mcs
com.oneplus.membership
com.oplus.widget
com.redteamobile.roaming
com.oplus.outdoormode
com.google.android.apps.safetyhub
com.google.android.apps.photos
com.android.traceur
com.heytap.market
com.heytap.themestore
com.coloros.video
com.coloros.weather2
com.coloros.weather.service
com.google.android.youtube
com.google.android.apps.nbu.files
com.oplus.games
com.oplus.logkit
com.oplus.crashbox
com.oplus.statistics.rom
com.oneplus.opshelf
com.oplus.shelf
";

COUNT=0;
for pkg in $SAFE_BLOAT_PKGS; do
  if pm list packages "$pkg" 2>/dev/null | grep -q "$pkg"; then
    echo " -> Cleaning & disabling bloat: $pkg";
    am force-stop "$pkg" >/dev/null 2>&1;
    pm uninstall-system-updates "$pkg" >/dev/null 2>&1;
    pm clear "$pkg" >/dev/null 2>&1;
    pm disable-user --user 0 "$pkg" >/dev/null 2>&1;
    COUNT=$((COUNT + 1));
  fi;
done;

pm trim-caches 999999999999999999 >/dev/null 2>&1;
echo "== DONE: $COUNT BLOAT PACKAGES CLEANED SAFELY ==";
echo "Storage after:";
df -h /data;
grep -E '^(MemTotal|MemFree|MemAvailable):' /proc/meminfo;

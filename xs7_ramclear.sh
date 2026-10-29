#!/system/bin/sh
# =========================================================================
# Project   : mikey-7x/Termux-projects — Ultra RAM & App Cache Purge
# Script    : xs7_ramclear.sh
# Author    : mikey-7x (https://github.com/mikey-7x)
# Target    : OnePlus 13R (CPH2691) & Android 12+ Devices (via aShell/ADB)
# Purpose   : Frees up to 6.3+ GB RAM for xs-7 & alfa5 XFCE4 desktop.
#             Enforces ActivityManager empty-process eviction (5s), cancels
#             all background JobScheduler jobs, and blocks BOOT_COMPLETED,
#             START_FOREGROUND, WAKE_LOCK, and RUN_ANY_IN_BACKGROUND for all
#             unopened apps (Facebook, Google Drive, Opera, Instagram, etc.)
#             while keeping WhatsApp notifications, Gemini, Termux, and
#             Termux:X11 100% active.
# Execution : sh /storage/emulated/0/xs7-ramclear.sh
# =========================================================================

echo "== [1/5] PURGING ALL ANDROID APP CACHES ==";
pm trim-caches 999999999999999999 >/dev/null 2>&1;
cmd package trim-caches 999999999999999999 internal >/dev/null 2>&1;
rm -rf /storage/emulated/0/Android/data/*/cache/* 2>/dev/null;
rm -rf /storage/emulated/0/Android/data/*/code_cache/* 2>/dev/null;
rm -rf /data/local/tmp/* 2>/dev/null;

echo "== [2/5] ENFORCING STRICT ACTIVITYMANAGER BACKGROUND CAPS ==";
/system/bin/device_config set_sync_disabled_for_tests persistent >/dev/null 2>&1;
/system/bin/device_config put activity_manager max_phantom_processes 2147483647 >/dev/null 2>&1;
settings put global max_phantom_processes 2147483647 >/dev/null 2>&1;
/system/bin/device_config put activity_manager_native_boot use_freezer true >/dev/null 2>&1;
settings put global cached_apps_freezer enabled >/dev/null 2>&1;
/system/bin/device_config put activity_manager max_cached_processes 4 >/dev/null 2>&1;
/system/bin/device_config put activity_manager max_empty_time_millis 5000 >/dev/null 2>&1;
/system/bin/device_config put activity_manager bg_auto_restricted_bucket_on_bg_restricted true >/dev/null 2>&1;

echo "== [3/5] DISABLING AI, META & OPLUS TELEMETRY DAEMONS ==";
for sys_pkg in com.google.android.aicore com.facebook.services com.facebook.system com.facebook.appmanager com.heytap.cloud com.heytap.mcs com.heytap.accessory com.heytap.habit.analysis com.oplus.stdid com.oplus.logkit com.oplus.crashbox com.oplus.statistics.rom com.oplus.lfeh com.coloros.activation; do
  pm disable-user --user 0 "$sys_pkg" >/dev/null 2>&1;
  am force-stop "$sys_pkg" >/dev/null 2>&1;
done;

echo "== [4/5] ALLOWING WHATSAPP & GEMINI, HARD-BLOCKING ALL UNOPENED APPS ==";
for keep_pkg in com.termux com.termux.x11 com.termux.api com.whatsapp com.whatsapp.w4b com.google.android.apps.bard com.google.android.googlequicksearchbox com.google.android.tts; do
  dumpsys deviceidle whitelist +"$keep_pkg" >/dev/null 2>&1;
  cmd appops set "$keep_pkg" BOOT_COMPLETED allow >/dev/null 2>&1;
  cmd appops set "$keep_pkg" RUN_IN_BACKGROUND allow >/dev/null 2>&1;
  cmd appops set "$keep_pkg" RUN_ANY_IN_BACKGROUND allow >/dev/null 2>&1;
  cmd appops set "$keep_pkg" WAKE_LOCK allow >/dev/null 2>&1;
  cmd appops set "$keep_pkg" START_FOREGROUND allow >/dev/null 2>&1;
  am set-inactive "$keep_pkg" false >/dev/null 2>&1;
done;

for pkg in $(pm list packages -3 2>/dev/null | cut -d: -f2); do
  case "$pkg" in
    com.termux*|in.sunilpaulmathew.ashell*|moe.shizuku.privileged.api*|com.whatsapp*|com.google.android.apps.bard*) continue ;;
  esac;
  cmd appops set "$pkg" BOOT_COMPLETED ignore >/dev/null 2>&1;
  cmd appops set "$pkg" RUN_IN_BACKGROUND ignore >/dev/null 2>&1;
  cmd appops set "$pkg" RUN_ANY_IN_BACKGROUND ignore >/dev/null 2>&1;
  cmd appops set "$pkg" WAKE_LOCK ignore >/dev/null 2>&1;
  cmd appops set "$pkg" START_FOREGROUND ignore >/dev/null 2>&1;
  cmd jobscheduler cancel "$pkg" >/dev/null 2>&1;
  am set-standby-bucket "$pkg" restricted >/dev/null 2>&1;
  am set-inactive "$pkg" true >/dev/null 2>&1;
  am force-stop "$pkg" >/dev/null 2>&1;
done;

for gpkg in com.google.android.apps.docs com.google.android.youtube com.google.android.apps.photos com.google.android.apps.maps com.android.chrome com.google.android.videos com.google.android.music; do
  cmd appops set "$gpkg" BOOT_COMPLETED ignore >/dev/null 2>&1;
  cmd appops set "$gpkg" RUN_IN_BACKGROUND ignore >/dev/null 2>&1;
  cmd appops set "$gpkg" RUN_ANY_IN_BACKGROUND ignore >/dev/null 2>&1;
  cmd appops set "$gpkg" WAKE_LOCK ignore >/dev/null 2>&1;
  cmd appops set "$gpkg" START_FOREGROUND ignore >/dev/null 2>&1;
  cmd jobscheduler cancel "$gpkg" >/dev/null 2>&1;
  am set-standby-bucket "$gpkg" restricted >/dev/null 2>&1;
  am set-inactive "$gpkg" true >/dev/null 2>&1;
  am force-stop "$gpkg" >/dev/null 2>&1;
done;

echo "== [5/5] EVICTING CACHED PROCESSES & GPU BUFFERS ==";
am kill-all >/dev/null 2>&1;
am send-trim-memory com.android.systemui RUNNING_CRITICAL >/dev/null 2>&1;
am send-trim-memory com.android.launcher COMPLETE >/dev/null 2>&1;

echo "== FREE RAM AFTER ULTRA PURGE ==";
grep -E '^(MemTotal|MemFree|MemAvailable|SwapFree):' /proc/meminfo;
echo "== FREE STORAGE AFTER APP CACHE PURGE ==";
df -h /data;

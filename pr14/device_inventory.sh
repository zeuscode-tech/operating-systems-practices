#!/usr/bin/env bash
set -euo pipefail

echo '=== ОС и ядро ==='
uname -a
echo
echo '=== Блочные устройства ==='
if command -v lsblk >/dev/null 2>&1; then
    lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,ROTA
else
    diskutil list 2>/dev/null || true
fi
echo
echo '=== Смонтированные файловые системы ==='
df -h
echo
echo '=== Устройства ввода-вывода ==='
if test -r /proc/devices; then
    cat /proc/devices
else
    echo '/proc/devices доступен только в Linux'
fi

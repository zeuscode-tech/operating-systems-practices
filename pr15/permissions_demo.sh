#!/usr/bin/env bash
set -euo pipefail

GROUP=pr15share
USER_A=pr15alice
USER_B=pr15bob
ROOT=/tmp/pr15-shared

test "$(uname -s)" = Linux || { echo 'Нужен Linux' >&2; exit 1; }
test "$(id -u)" -eq 0 || { echo "Запустите через sudo: $0 setup|cleanup" >&2; exit 1; }

case "${1:-}" in
    setup)
        getent group "$GROUP" >/dev/null || groupadd "$GROUP"
        id "$USER_A" >/dev/null 2>&1 || useradd -M -s /usr/sbin/nologin "$USER_A"
        id "$USER_B" >/dev/null 2>&1 || useradd -M -s /usr/sbin/nologin "$USER_B"
        usermod -aG "$GROUP" "$USER_A"
        usermod -aG "$GROUP" "$USER_B"
        install -d -o "$USER_A" -g "$GROUP" -m 2770 "$ROOT"
        sudo -u "$USER_A" sh -c "printf 'общие данные\n' > '$ROOT/data.txt'"
        sudo -u "$USER_B" cat "$ROOT/data.txt"
        ls -ld "$ROOT"; ls -l "$ROOT/data.txt"
        echo "Готово. Очистка: sudo $0 cleanup"
        ;;
    cleanup)
        rm -rf "$ROOT"
        userdel "$USER_A" 2>/dev/null || true
        userdel "$USER_B" 2>/dev/null || true
        groupdel "$GROUP" 2>/dev/null || true
        echo 'Учебные пользователи и каталог удалены'
        ;;
    *) echo "Использование: sudo $0 setup|cleanup" >&2; exit 2 ;;
esac

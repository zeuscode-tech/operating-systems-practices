# Практическая работа №15 — защита, контейнеры и виртуализация

## Цель

Показать права доступа Linux, изоляцию контейнера, ограничения ресурсов и отличие контейнера от виртуальной машины.

## Уровень A

`permissions_demo.sh` создаёт двух временных пользователей, общую группу и каталог с setgid. Скрипт требует явных команд `setup` и `cleanup` и предназначен для учебной Ubuntu.

`app.py` — проверяемый HTTP-сервис с `/health` и `/info`. Dockerfile запускает его непривилегированным UID 10001.

```bash
python3 -m unittest -v test_app.py
docker build -t pr15-app .
docker run --rm -p 8080:8080 pr15-app
```

## Уровень B

- `compose.yaml` удаляет capabilities, включает `no-new-privileges`, read-only rootfs и лимиты CPU/RAM.
- `container_limits.sh` показывает фактические cgroup-ограничения.
- `isolation_demo.sh` сравнивает отдельный PID namespace и `--pid=host`.
- `benchmark_isolation.sh` измеряет время старта контейнера.

Контейнер изолирует процессы, сеть, файловую систему и ресурсы, но использует ядро хоста. VM запускает отдельное ядро и даёт более сильную, но более дорогую изоляцию.

## Уровень C

`container_from_scratch.sh` демонстрирует основу контейнера через `unshare`, PID/mount/UTS namespaces и `chroot` поверх минимального BusyBox rootfs. Запуск возможен только в отдельной Linux VM от root.

## Безопасность

Контейнер не является автоматической границей абсолютной безопасности. Использованы non-root, минимальный образ, read-only rootfs, сброс capabilities, запрет повышения привилегий и лимиты cgroups.

## Проверка

```bash
./run_all.sh
docker compose config
```

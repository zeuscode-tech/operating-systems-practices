#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null || { echo 'Нужен Docker' >&2; exit 1; }
IMAGE=pr15-app
docker build -t "$IMAGE" .
docker run --rm --name pr15-limits --memory=128m --cpus=0.5 -d "$IMAGE" >/dev/null
trap 'docker rm -f pr15-limits >/dev/null 2>&1 || true' EXIT
sleep 2
docker stats --no-stream pr15-limits
docker inspect pr15-limits --format 'Memory={{.HostConfig.Memory}} NanoCPUs={{.HostConfig.NanoCpus}} PidMode={{.HostConfig.PidMode}}'

#!/bin/sh
set -eu

image="${1:-app-poly-gitops-fastapi:test}"
container_id="$(docker run -d --network none "$image")"

cleanup() {
  docker logs "$container_id" 2>/dev/null || true
  docker rm -f "$container_id" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in $(seq 1 30); do
  if [ "$(docker inspect -f '{{.State.Running}}' "$container_id")" != true ]; then
    echo "container exited before becoming healthy" >&2
    exit 1
  fi

  if docker exec "$container_id" .venv/bin/python -c \
    'import json, urllib.request; assert json.load(urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1)) == {"status": "ok"}' \
    >/dev/null 2>&1; then
    exit 0
  fi
  sleep 1
done

echo "container did not become healthy without runtime network access" >&2
exit 1

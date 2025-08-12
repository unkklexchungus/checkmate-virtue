#!/usr/bin/env bash
set -euo pipefail

# Phased microservice control for inspections
# Usage:
#   ./scripts/inspection_services.sh start-core
#   ./scripts/inspection_services.sh start-optional
#   ./scripts/inspection_services.sh stop-all
#   ./scripts/inspection_services.sh status
#   ./scripts/inspection_services.sh logs [service-name]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Required command not found: $1"
    exit 1
  fi
}

require docker
if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
  echo "❌ Docker Compose is required"
  exit 1
fi

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  else
    docker-compose "$@"
  fi
}

ensure_env() {
  if [[ ! -f "$ROOT_DIR/.env" ]]; then
    echo "📝 Creating .env from env.example"
    cp "$ROOT_DIR/env.example" "$ROOT_DIR/.env"
  fi
  # Ensure APP_BASE_URL exists (fallback for local dev)
  if ! grep -qE '^APP_BASE_URL=' "$ROOT_DIR/.env"; then
    echo "APP_BASE_URL=http://127.0.0.1:8000" >> "$ROOT_DIR/.env"
  fi
}

wait_http_ok() {
  local name="$1" url="$2" timeout="${3:-60}"
  echo -n "⏳ Waiting for $name at $url ..."
  local start=$(date +%s)
  until curl -fsS "$url" >/dev/null 2>&1; do
    sleep 1
    local now=$(date +%s)
    if (( now - start >= timeout )); then
      echo " ❌ timeout"
      return 1
    fi
    echo -n "."
  done
  echo " ✅"
  return 0
}

start_core() {
  ensure_env
  echo "🚀 Starting core inspection services"
  # Core set: database/cache + essentials for inspections
  compose up -d postgres redis vehicle-service customer-service api-gateway
  # Health checks (best-effort)
  wait_http_ok "Vehicle Service" "http://localhost:8003/healthz" 90 || true
  wait_http_ok "Customer Service" "http://localhost:8002/healthz" 90 || true
  wait_http_ok "API Gateway" "http://localhost:8080/healthz" 90 || true
  echo "✅ Core services ready (or running health attempts)."
}

start_optional() {
  ensure_env
  echo "🚀 Starting optional services (on-demand)"
  compose up -d notification-service workshop-service inventory-service appointment-service
  # Health checks (best-effort)
  wait_http_ok "Workshop Service" "http://localhost:8005/healthz" 90 || true
  wait_http_ok "Inventory Service" "http://localhost:8006/healthz" 90 || true
  # appointment-service and notification-service ports may differ; skip strict checks
  echo "✅ Optional services started (best-effort health)."
}

stop_all() {
  echo "🛑 Stopping all services"
  compose down
}

status() {
  echo "📦 Docker services:"
  compose ps
}

logs() {
  local svc="${1:-}"
  if [[ -z "$svc" ]]; then
    echo "🔎 Tailing all logs (Ctrl-C to stop)"
    compose logs -f
  else
    echo "🔎 Tailing logs for: $svc (Ctrl-C to stop)"
    compose logs -f "$svc"
  fi
}

case "${1:-}" in
  start-core) start_core ;;
  start-optional) start_optional ;;
  stop-all) stop_all ;;
  status) status ;;
  logs) shift; logs "${1:-}" ;;
  *)
    cat <<EOF
Usage:
  $0 start-core        # postgres, redis, vehicle-service, customer-service, api-gateway
  $0 start-optional    # notification-service, workshop-service, inventory-service, appointment-service
  $0 status            # show compose status
  $0 logs [service]    # follow logs
  $0 stop-all          # stop everything
EOF
    exit 1
    ;;
esac

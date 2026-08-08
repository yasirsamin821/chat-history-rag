#!/usr/bin/env bash
set -euo pipefail

# --- fill these in -----------------------------------------------------
PROJECT_DIR="/home/samin96/code_folders/rag_new2"
VENV_DIR="/home/samin96/code_folders/rag_new2/venv"
FRONTEND_REPO_DIR="/home/samin96/cloudfare_deployment"
API_PORT=8000
# -------------------------------------------------------------------------

echo "==> Stopping any previous instance..."
pkill -f "uvicorn src.app.rag.main:app" 2>/dev/null || true
pkill -f "cloudflared tunnel --url http://localhost:$API_PORT" 2>/dev/null || true
sleep 2

echo "==> Starting the API..."
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"
nohup uvicorn src.app.rag.main:app --host 0.0.0.0 --port "$API_PORT" \
  > "$PROJECT_DIR/deployment/uvicorn.log" 2>&1 &

echo "==> Waiting for the API to become healthy..."
for i in $(seq 1 30); do
  if curl -s "http://localhost:$API_PORT/health" > /dev/null; then
    echo "    API is up."
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: API did not become healthy in time. Check $PROJECT_DIR/deployment/uvicorn.log"
    exit 1
  fi
  sleep 2
done

echo "==> Opening Cloudflare tunnel..."
nohup cloudflared tunnel --url "http://localhost:$API_PORT" \
  > "$PROJECT_DIR/deployment/cloudflared.log" 2>&1 &

echo "==> Waiting for tunnel URL..."
TUNNEL_URL=""
for i in $(seq 1 30); do
  TUNNEL_URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$PROJECT_DIR/deployment/cloudflared.log" | head -n1 || true)
  if [ -n "$TUNNEL_URL" ]; then
    break
  fi
  sleep 2
done

if [ -z "$TUNNEL_URL" ]; then
  echo "ERROR: Could not find tunnel URL. Check $PROJECT_DIR/deployment/cloudflared.log"
  exit 1
fi

echo "==> New tunnel URL: $TUNNEL_URL"

echo "==> Publishing to GitHub..."
cd "$FRONTEND_REPO_DIR"
git pull --quiet
cat > config.json <<EOF
{
  "apiUrl": "$TUNNEL_URL",
  "updatedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
git add config.json
git commit -m "update tunnel url: $TUNNEL_URL" --quiet
git push --quiet

echo "==> Done."
echo "    Backend:  $TUNNEL_URL"
echo "    Frontend: https://yasirsamin821.github.io/cloudfare_deployment/rag_chat_ui.html"
echo "    (your friend's tab picks up the new URL within 60s, or on refresh)"
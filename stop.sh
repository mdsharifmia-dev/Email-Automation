#!/bin/bash
# Stop AI Email Agent

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$DIR/agent.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️  AI Email Agent is not running (no PID file found)."
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    echo "🛑 Stopping AI Email Agent (PID: $PID)..."
    kill "$PID"
    sleep 1
    if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID"
    fi
    echo "✅ AI Email Agent stopped."
else
    echo "ℹ️  Process $PID is not running."
fi

rm -f "$PID_FILE"

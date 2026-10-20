#!/bin/bash
# Start AI Email Agent in background

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PID_FILE="$DIR/agent.pid"
LOG_FILE="$DIR/agent.log"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "⚠️  AI Email Agent is already running with PID: $PID"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

echo "🚀 Starting AI Email Agent in background..."
nohup python3 -u run_agent.py >> "$LOG_FILE" 2>&1 &
PID=$!
disown $PID
echo "$PID" > "$PID_FILE"

echo "✅ AI Email Agent started successfully with PID: $PID"
echo "📄 Logs: tail -f $LOG_FILE"

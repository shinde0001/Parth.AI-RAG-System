#!/bin/bash
echo "Starting Parth.AI RAG System..."

# Kill any existing server on port 8000 or 5173 to prevent address in use errors
fuser -k 8000/tcp > /dev/null 2>&1
fuser -k 5173/tcp > /dev/null 2>&1

# Start backend in the background
echo "Starting FastAPI backend on port 8000..."
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Start frontend in the background
echo "Starting Vite frontend on port 5173..."
cd frontend && npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "Waiting for AI backend to load models..."
while ! curl -s http://localhost:8000/api/v1/health > /dev/null; do
    sleep 1
done

echo ""
echo "========================================================"
echo "✅ Parth.AI is fully initialized & LIVE!"
echo "👉 Open the Dashboard here: http://localhost:5173"
echo "========================================================"
echo ""
echo "Press [CTRL+C] to stop the servers."

# Trap Ctrl+C to kill both background processes
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Keep script running while background tasks are active
wait

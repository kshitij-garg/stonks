#!/bin/bash

echo ""
echo "===================================="
echo "  Stonks by KG - Starting..."
echo "===================================="
echo ""

# Start backend
echo "Starting Backend Server..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Start frontend
echo "Starting Frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait and open browser
sleep 5
echo "Opening browser..."

# Open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5173
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:5173
fi

echo ""
echo "===================================="
echo "  Stonks by KG is running!"
echo "===================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait

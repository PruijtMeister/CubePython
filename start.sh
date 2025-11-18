#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}[${1}]${NC} ${3}"
}

# Function to cleanup processes on exit
cleanup() {
    print_message "SHUTDOWN" "$YELLOW" "Stopping services..."

    if [ ! -z "$BACKEND_PID" ]; then
        print_message "BACKEND" "$RED" "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        print_message "FRONTEND" "$RED" "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi

    # Wait a moment for graceful shutdown
    sleep 1

    # Force kill if still running
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill -9 $BACKEND_PID 2>/dev/null
    fi

    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill -9 $FRONTEND_PID 2>/dev/null
    fi

    print_message "SHUTDOWN" "$GREEN" "All services stopped"
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

print_message "STARTUP" "$GREEN" "Starting CubePython services..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_message "VENV" "$YELLOW" "Virtual environment not activated. Activating..."

    # Try to activate .venv
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        print_message "VENV" "$GREEN" "Virtual environment activated"
    elif [ -f "backend/venv/bin/activate" ]; then
        source backend/venv/bin/activate
        print_message "VENV" "$GREEN" "Virtual environment activated"
    else
        print_message "VENV" "$RED" "No virtual environment found. Please run setup.sh first."
        exit 1
    fi
fi

# Start the backend
print_message "BACKEND" "$BLUE" "Starting backend on http://localhost:8000"
cd backend
python run.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for the backend to start
sleep 2

# Check if backend is still running
if ! ps -p $BACKEND_PID > /dev/null; then
    print_message "BACKEND" "$RED" "Failed to start backend. Check backend.log for errors."
    cat backend.log
    exit 1
fi

print_message "BACKEND" "$GREEN" "Backend started (PID: $BACKEND_PID)"
print_message "BACKEND" "$BLUE" "API docs available at http://localhost:8000/docs"

# Start the frontend
print_message "FRONTEND" "$BLUE" "Starting frontend on http://localhost:3000"
cd frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

print_message "FRONTEND" "$GREEN" "Frontend started (PID: $FRONTEND_PID)"

# Show status
echo ""
print_message "STATUS" "$GREEN" "All services running!"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}  Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}  API Docs:${NC} http://localhost:8000/docs"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
print_message "INFO" "$YELLOW" "Press Ctrl+C to stop all services"
echo ""
print_message "LOGS" "$BLUE" "Backend logs: tail -f backend.log"
print_message "LOGS" "$BLUE" "Frontend logs: tail -f frontend.log"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID

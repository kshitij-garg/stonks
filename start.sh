#!/usr/bin/env bash
echo "============================================================="
echo "  QuantRebalance - Institutional Portfolio Engine"
echo "============================================================="

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Starting QuantRebalance Backend on http://127.0.0.1:5000..."
$PYTHON_CMD app.py

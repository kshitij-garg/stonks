#!/bin/bash

echo ""
echo "===================================="
echo "  Stonks by KG - One Click Setup"
echo "===================================="
echo ""

# Check Python
echo "[1/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found! Please install Python 3.8+"
    exit 1
fi
echo "      Python found!"

# Check Node.js
echo "[2/5] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found! Please install Node.js 16+"
    exit 1
fi
echo "      Node.js found!"

# Install Python dependencies
echo "[3/5] Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt -q
cd ..
echo "      Python dependencies installed!"

# Install Node dependencies
echo "[4/5] Installing Node.js dependencies..."
npm install --silent
echo "      Node.js dependencies installed!"

echo ""
echo "===================================="
echo "  Setup Complete!"
echo "===================================="
echo ""
echo "To start the application, run: ./start.sh"
echo ""

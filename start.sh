#!/bin/bash

# Start FastAPI in the background
echo "Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit on the port provided by Render
echo "Starting Streamlit frontend..."
streamlit run frontend/dashboard.py --server.port $PORT --server.address 0.0.0.0

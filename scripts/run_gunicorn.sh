# scripts/run_gunicorn.sh
#!/bin/bash
# Ejecutar en Linux/Mac, para Windows usar .bat equivalente

export PYTHONPATH=.
gunicorn api.app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

@echo off
set PYTHONPATH=.
gunicorn api.app:app ^
    --workers 4 ^
    --worker-class uvicorn.workers.UvicornWorker ^
    --bind 0.0.0.0:8000 ^
    --timeout 120 ^
    --access-logfile - ^
    --error-logfile -
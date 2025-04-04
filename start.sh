#!/bin/bash
cd /work
PYTHONPATH=$PYTHONPATH:/work python app/main.py --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
#!/bin/bash

# Start the first process
celery -A src.celery_worker worker &

celery -A src.celery_worker beat &

# Start the second process
uvicorn src.main:app --reload --host 0.0.0.0 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?

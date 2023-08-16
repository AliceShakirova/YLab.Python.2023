#!/bin/bash

celery -A src.celery_worker worker -B &
uvicorn src.main:app --reload --host 0.0.0.0 &

wait -n

# Exit with status of process that exited first
exit $?

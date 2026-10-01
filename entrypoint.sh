#!/bin/sh

set -e

alembic upgrade head

exec uvicorn --host 0.0.0.0 --port 8000 app.main:app
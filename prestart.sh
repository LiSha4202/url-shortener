#!/usr/bin/env bash

set -e

echo "Running alembic..."
alembic revision --autogenerate -m "Create User; Link Tables"
alembic upgrade head
echo "Done"

exec "$@"
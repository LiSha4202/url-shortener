#!/usr/bin/env bash

set -e

echo "Running alembic..."
alembic upgrade head
echo "Done"

exec "$@"
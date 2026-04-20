#!/usr/bin/env bash
#
# Gate Profile: Docker
# ====================
# Docker verification: build image + run tests in container
#
# Usage in config.env:
#   GATE_CMD="source $BASE/profiles/gate-docker.sh"
#
# Optional env vars:
#   DOCKER_IMAGE_NAME - name for the built image (default: labloop-test)
#   DOCKER_TEST_CMD   - command to run tests (default: npm test)
#
set -euo pipefail

echo "=== Gate: Docker ==="

IMAGE_NAME="${DOCKER_IMAGE_NAME:-labloop-test}"
TEST_CMD="${DOCKER_TEST_CMD:-npm test}"

# Build
echo ">>> Building Docker image: $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" . 2>&1 || exit 1

# Run tests
echo ">>> Running tests in container..."
docker run --rm "$IMAGE_NAME" $TEST_CMD 2>&1 || exit 1

echo "=== Gate: Docker PASSED ==="

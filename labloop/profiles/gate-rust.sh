#!/usr/bin/env bash
#
# Gate Profile: Rust
# ==================
# Rust verification: clippy + test + build
#
# Usage in config.env:
#   GATE_CMD="source $BASE/profiles/gate-rust.sh"
#
set -euo pipefail

echo "=== Gate: Rust ==="

# Format check
echo ">>> Checking formatting..."
cargo fmt --check || exit 1

# Clippy
echo ">>> Running clippy..."
cargo clippy -- -D warnings || exit 1

# Tests
echo ">>> Running tests..."
cargo test 2>&1 || exit 1

# Build
echo ">>> Building release..."
cargo build --release 2>&1 || exit 1

echo "=== Gate: Rust PASSED ==="

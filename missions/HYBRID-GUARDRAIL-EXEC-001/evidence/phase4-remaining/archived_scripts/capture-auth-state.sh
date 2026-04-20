#!/usr/bin/env bash
# tools/validation/capture-auth-state.sh
# V3: One-time capture of authenticated browser state

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

OUTPUT_DIR="artifacts/auth"
mkdir -p "$OUTPUT_DIR"

echo "═══ CAPTURE AUTH STATE ═══"
echo ""

if [ -z "${DASHBOARD_TEST_USER:-}" ] || [ -z "${DASHBOARD_TEST_PASS:-}" ]; then
  echo "Set DASHBOARD_TEST_USER and DASHBOARD_TEST_PASS environment variables"
  exit 1
fi

cat > "$OUTPUT_DIR/capture-auth.js" << 'JSEOF'
const { chromium } = require('playwright');

const DASHBOARD_URL = process.env.DASHBOARD_URL || 'http://localhost:3003';
const TEST_USER = process.env.DASHBOARD_TEST_USER;
const TEST_PASS = process.env.DASHBOARD_TEST_PASS;
const OUTPUT_FILE = process.env.OUTPUT_FILE || 'storageState.json';

async function captureAuth() {
  const browser = await chromium.launch({ headless: false }); // Show browser for debugging
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log(`Navigating to ${DASHBOARD_URL}/login...`);
  await page.goto(`${DASHBOARD_URL}/login`, { waitUntil: 'networkidle' });

  console.log('Filling login form...');
  await page.fill('input[name="email"], input[type="email"]', TEST_USER);
  await page.fill('input[name="password"], input[type="password"]', TEST_PASS);

  console.log('Submitting...');
  await page.click('button[type="submit"]');

  // Wait for redirect after login
  await page.waitForURL('**/*', { timeout: 30000 });
  console.log(`Logged in, now at: ${page.url()}`);

  // Save storage state
  await context.storageState({ path: OUTPUT_FILE });
  console.log(`Auth state saved to ${OUTPUT_FILE}`);

  await browser.close();
}

captureAuth().catch(console.error);
JSEOF

DASHBOARD_URL="$DASHBOARD_URL" \
  DASHBOARD_TEST_USER="$DASHBOARD_TEST_USER" \
  DASHBOARD_TEST_PASS="$DASHBOARD_TEST_PASS" \
  OUTPUT_FILE="$OUTPUT_DIR/storageState.json" \
  node "$OUTPUT_DIR/capture-auth.js"

echo ""
echo "✅ Auth state captured to: $OUTPUT_DIR/storageState.json"
echo "   This file is gitignored but used by network capture"

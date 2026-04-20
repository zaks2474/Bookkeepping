#!/usr/bin/env bash
set -euo pipefail

RUN_TS="$(date +%Y%m%d-%H%M%S)"
RUN_ID="QA-VERIFY-001-${RUN_TS}"

OUT_BASE="/home/zaks/bookkeeping/qa-results"
TEST_DIR="${OUT_BASE}/${RUN_ID}"

mkdir -p "${TEST_DIR}"

echo "QA-VERIFY-001 run starting"
echo "RUN_ID=${RUN_ID}"
echo "TEST_DIR=${TEST_DIR}"
echo

set +e
python3 /home/zaks/bookkeeping/docs/qa_verify_001/qa_verify_001.py \
  --run-id "${RUN_ID}" \
  --test-dir "${TEST_DIR}" \
  | tee "${TEST_DIR}/runner.log"
PY_STATUS="${PIPESTATUS[0]}"
set -e

# Copy report into docs for durable discoverability
REPORT_SRC="${TEST_DIR}/QA_VERIFICATION_REPORT.md"
REPORT_DST="/home/zaks/bookkeeping/docs/qa_verify_001/QA_VERIFICATION_REPORT_${RUN_ID}.md"

if [[ -f "${REPORT_SRC}" ]]; then
  cp -a "${REPORT_SRC}" "${REPORT_DST}"
  echo
  echo "Report copied to docs:"
  echo "  ${REPORT_DST}"
else
  echo
  echo "ERROR: QA_VERIFICATION_REPORT.md not found at ${REPORT_SRC}"
  exit 1
fi

echo
echo "Run complete."
echo "Artifacts: ${TEST_DIR}"

if [[ "${PY_STATUS}" != "0" ]]; then
  echo
  echo "WARNING: QA runner exited non-zero (${PY_STATUS}). See report for failures."
fi

exit "${PY_STATUS}"

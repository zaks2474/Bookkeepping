#!/usr/bin/env bash
#
# Lab Loop Task Generator
# =======================
# Creates a new task with scaffold files
#
# Usage: labloop-new.sh <TASK_ID> [--repo PATH] [--gate CMD]
#
set -euo pipefail

BASE="/home/zaks/bookkeeping/labloop"

# Parse arguments
TASK_ID=""
REPO_DIR=""
GATE_CMD=""
PROFILE=""

# Available profiles
PROFILES_DIR="$BASE/profiles"

show_profiles() {
  echo "Available gate profiles:"
  echo ""
  for profile in "$PROFILES_DIR"/gate-*.sh; do
    if [[ -f "$profile" ]]; then
      local name
      name=$(basename "$profile" .sh | sed 's/gate-//')
      local desc
      desc=$(grep -m1 "^# Gate Profile:" "$profile" 2>/dev/null | sed 's/^# Gate Profile: //' || echo "")
      printf "  %-20s %s\n" "$name" "$desc"
    fi
  done
  echo ""
  echo "Usage: labloop new <TASK_ID> --profile <name>"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_DIR="$2"
      shift 2
      ;;
    --gate)
      GATE_CMD="$2"
      shift 2
      ;;
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --list-profiles)
      show_profiles
      exit 0
      ;;
    -h|--help)
      echo "Usage: labloop-new.sh <TASK_ID> [--repo PATH] [--gate CMD] [--profile NAME]"
      echo ""
      echo "Creates a new task folder with scaffold files."
      echo ""
      echo "Options:"
      echo "  --repo PATH      Repository path (prompted if not provided)"
      echo "  --gate CMD       Gate command (prompted if not provided)"
      echo "  --profile NAME   Use a predefined gate profile (e.g., python-fast, nextjs)"
      echo "  --list-profiles  Show available gate profiles"
      echo ""
      echo "Examples:"
      echo "  labloop new phase18 --repo /home/zaks/zakops-agent-api --gate 'pytest tests/'"
      echo "  labloop new phase18 --repo /home/zaks/zakops-agent-api --profile python-fast"
      echo "  labloop new myapp --repo /home/zaks/myapp --profile nextjs"
      echo ""
      echo "Profiles available:"
      for profile in "$PROFILES_DIR"/gate-*.sh; do
        if [[ -f "$profile" ]]; then
          echo "  - $(basename "$profile" .sh | sed 's/gate-//')"
        fi
      done
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      TASK_ID="$1"
      shift
      ;;
  esac
done

if [[ -z "$TASK_ID" ]]; then
  echo "Usage: labloop-new.sh <TASK_ID> [--repo PATH] [--gate CMD]"
  exit 1
fi

TASK_DIR="$BASE/tasks/$TASK_ID"

# Check if task already exists
if [[ -d "$TASK_DIR" ]]; then
  echo "ERROR: Task already exists: $TASK_DIR"
  echo "To start fresh, delete it first: rm -rf $TASK_DIR"
  exit 1
fi

# Interactive prompts if not provided
if [[ -z "$REPO_DIR" ]]; then
  echo -n "Repository path (e.g., /home/zaks/zakops-agent-api): "
  read -r REPO_DIR
fi

if [[ ! -d "$REPO_DIR" ]]; then
  echo "WARNING: Repository path does not exist: $REPO_DIR"
  echo -n "Continue anyway? [y/N]: "
  read -r confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    exit 1
  fi
fi

# If profile specified, use it to set GATE_CMD
if [[ -n "$PROFILE" ]]; then
  PROFILE_FILE="$PROFILES_DIR/gate-${PROFILE}.sh"
  if [[ -f "$PROFILE_FILE" ]]; then
    GATE_CMD="bash $PROFILE_FILE"
    echo "Using gate profile: $PROFILE"
  else
    echo "ERROR: Profile not found: $PROFILE"
    echo "Available profiles:"
    for p in "$PROFILES_DIR"/gate-*.sh; do
      if [[ -f "$p" ]]; then
        echo "  - $(basename "$p" .sh | sed 's/gate-//')"
      fi
    done
    exit 1
  fi
fi

if [[ -z "$GATE_CMD" ]]; then
  echo -n "Gate command (e.g., 'pytest tests/' or use --profile): "
  read -r GATE_CMD
fi

# Create task structure
echo "Creating task: $TASK_ID"
mkdir -p "$TASK_DIR"/{history,artifacts}

# Create config.env
cat > "$TASK_DIR/config.env" <<EOF
# Lab Loop Task Configuration
# Task: $TASK_ID
# Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Repository path
REPO_DIR="$REPO_DIR"

# Verification gate command (must exit 0 on success)
GATE_CMD="$GATE_CMD"

# Additional directories for Claude to read (comma-separated, optional)
CLAUDE_ADD_DIRS="/home/zaks/bookkeeping/docs"

# Maximum cycles before giving up (optional, default: 50)
# MAX_CYCLES=50
EOF

# Create mission.md template
cat > "$TASK_DIR/mission.md" <<'EOF'
# Mission: [TASK TITLE]

## Objective

[Describe what needs to be built or fixed]

## Background

[Provide context about the current state and why this task is needed]

## Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]

## Technical Requirements

[List specific technical requirements]

## References

- [Link to relevant docs or specs]
EOF

# Create acceptance.md template
cat > "$TASK_DIR/acceptance.md" <<'EOF'
# Acceptance Criteria

## Definition of Done

The task is complete when ALL of the following are true:

### Functional Requirements
- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Quality Gates
- [ ] All tests pass (`pytest tests/` or equivalent)
- [ ] No linting errors
- [ ] No type errors (if applicable)

### Spec Compliance
- [ ] Endpoints match specification
- [ ] Response schemas match specification
- [ ] Status codes match specification
- [ ] Authentication works as specified

## Verification Steps

1. [Step 1: How to verify]
2. [Step 2: How to verify]

## Gate Command

The verification gate command is:
```bash
# This is configured in config.env
```

This command must exit with code 0 for the task to pass.
EOF

# Create empty BUILDER_REPORT.md placeholder
cat > "$TASK_DIR/BUILDER_REPORT.md" <<'EOF'
# Builder Report

*This file will be populated by the Builder agent during the lab loop.*
EOF

echo ""
echo "========================================"
echo "Task created: $TASK_ID"
echo "========================================"
echo ""
echo "Directory: $TASK_DIR"
echo ""
echo "Files created:"
echo "  - config.env      (task configuration)"
echo "  - mission.md      (what to build - EDIT THIS)"
echo "  - acceptance.md   (how to verify - EDIT THIS)"
echo "  - BUILDER_REPORT.md (placeholder)"
echo "  - history/        (cycle history)"
echo "  - artifacts/      (gate artifacts)"
echo ""
echo "Next steps:"
echo "  1. Edit mission.md with your task description"
echo "  2. Edit acceptance.md with acceptance criteria"
echo "  3. Run: labloop.sh $TASK_ID"
echo ""

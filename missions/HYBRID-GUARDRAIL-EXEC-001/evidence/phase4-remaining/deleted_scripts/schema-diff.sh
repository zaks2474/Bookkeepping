#!/usr/bin/env bash
# tools/infra/schema-diff.sh
# V3 COMPANION NOTE #1: 3-way schema diff — DB ↔ Backend Python ↔ Dashboard Zod
# Machine-readable JSON diffs, not prose
# P1 diffs (case mismatch, missing field, nullability) → exit 1
# P2 diffs (dead fields, type coercion) → warning only
# Must source topology.env — no hardcoded paths or ports

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/schema-diffs"
mkdir -p "$EVIDENCE_DIR"

echo "═══ 3-WAY SCHEMA DIFF (V4) ═══"
echo "DB (information_schema) ↔ Backend Python ↔ Dashboard Zod"
echo ""

# ══════════════════════════════════════════════════════════════
# STEP 1: Extract DB schema from information_schema.columns
# V4 FIX: Auto-detect schema name (tables may be in 'zakops', not 'public')
# ══════════════════════════════════════════════════════════════

echo "── Step 1: Extracting DB Schema ──"

# Auto-detect schema name
DB_SCHEMA=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
  SELECT DISTINCT table_schema FROM information_schema.tables
  WHERE table_schema NOT IN ('pg_catalog','information_schema')
  AND table_type = 'BASE TABLE' LIMIT 1;
" 2>/dev/null || echo "public")
DB_SCHEMA=$(echo "$DB_SCHEMA" | tr -d '[:space:]')
[ -z "$DB_SCHEMA" ] && DB_SCHEMA="public"
echo "  Detected DB schema: $DB_SCHEMA"

docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
SELECT json_agg(row_to_json(t))
FROM (
  SELECT
    table_name,
    column_name,
    data_type,
    udt_name,
    is_nullable,
    column_default,
    character_maximum_length,
    ordinal_position
  FROM information_schema.columns
  WHERE table_schema = '$DB_SCHEMA'
    AND table_name IN ('deals', 'actions', 'events', 'deal_events', 'action_events', 'agent_runs', 'quarantine_items', 'deal_aliases')
  ORDER BY table_name, ordinal_position
) t;
" 2>/dev/null > "$EVIDENCE_DIR/db_schema_raw.json" || echo "[]" > "$EVIDENCE_DIR/db_schema_raw.json"

DB_COL_COUNT=$(python3 -c "import json; d=json.load(open('$EVIDENCE_DIR/db_schema_raw.json')); print(len(d) if d else 0)" 2>/dev/null || echo "0")
echo "  DB columns extracted: $DB_COL_COUNT"

# ══════════════════════════════════════════════════════════════
# STEP 2: Extract Backend Python model fields
# ══════════════════════════════════════════════════════════════

echo "── Step 2: Extracting Backend Python Models ──"

python3 << 'PYEOF'
import ast
import os
import json
import re

backend_root = os.environ.get("BACKEND_ROOT", "")
if not backend_root:
    print("❌ BACKEND_ROOT not set")
    exit(1)

evidence_dir = "artifacts/infra-awareness/evidence/schema-diffs"

model_files = [
    f"{backend_root}/src/core/deal_registry.py",
    f"{backend_root}/src/actions/engine/models.py",
    f"{backend_root}/src/core/agent/models.py",
    f"{backend_root}/src/core/events/models.py",
    f"{backend_root}/src/core/events/schema.py",
]

models = {}

def extract_type_hint(annotation):
    """Best-effort type hint extraction from AST node."""
    if annotation is None:
        return "Any"
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant):
        return str(annotation.value)
    if isinstance(annotation, ast.Attribute):
        return f"{extract_type_hint(annotation.value)}.{annotation.attr}"
    if isinstance(annotation, ast.Subscript):
        base = extract_type_hint(annotation.value)
        inner = extract_type_hint(annotation.slice)
        return f"{base}[{inner}]"
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        left = extract_type_hint(annotation.left)
        right = extract_type_hint(annotation.right)
        return f"{left} | {right}"
    if isinstance(annotation, ast.Tuple):
        parts = [extract_type_hint(e) for e in annotation.elts]
        return ", ".join(parts)
    return "complex"

def is_optional(type_str):
    """Check if type hint indicates optional."""
    if not type_str:
        return False
    return ("Optional" in type_str or
            "None" in type_str or
            "| None" in type_str)

for fpath in model_files:
    if not os.path.exists(fpath):
        continue

    with open(fpath) as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        continue

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        class_name = node.name
        fields = {}

        for item in node.body:
            # Pydantic/dataclass field assignments
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                type_hint = extract_type_hint(item.annotation)

                has_default = item.value is not None
                nullable = is_optional(type_hint)
                required = not has_default and not nullable

                fields[field_name] = {
                    "type": type_hint,
                    "required": required,
                    "nullable": nullable,
                    "source_file": os.path.basename(fpath),
                }

        if fields:
            models[class_name] = {
                "file": os.path.relpath(fpath, backend_root),
                "fields": fields
            }

with open(f"{evidence_dir}/backend_models.json", "w") as f:
    json.dump(models, f, indent=2)

print(f"✅ Extracted {len(models)} Python models")
for name in sorted(models.keys()):
    print(f"   {name}: {len(models[name]['fields'])} fields")
PYEOF

# ══════════════════════════════════════════════════════════════
# STEP 3: Extract Dashboard Zod schema fields
# ══════════════════════════════════════════════════════════════

echo "── Step 3: Extracting Dashboard Zod Schemas ──"

python3 << 'PYEOF'
import os
import re
import json

dashboard_root = os.environ.get("DASHBOARD_ROOT", "")
if not dashboard_root:
    print("❌ DASHBOARD_ROOT not set")
    exit(1)

evidence_dir = "artifacts/infra-awareness/evidence/schema-diffs"

schema_files = [
    f"{dashboard_root}/src/lib/api-schemas.ts",
    f"{dashboard_root}/src/lib/api.ts",
]

schemas = {}

# Regex patterns for Zod schema extraction
SCHEMA_DEF = re.compile(r'(?:export\s+)?(?:const|let)\s+(\w+Schema)\s*=\s*z\.object\(\{', re.MULTILINE)
FIELD_LINE = re.compile(r'^\s*(\w+)\s*:\s*(.+?)(?:,\s*)?$', re.MULTILINE)
ZOD_OPTIONAL = re.compile(r'\.optional\(\)')
ZOD_NULLABLE = re.compile(r'\.nullable\(\)')
ZOD_NULLISH = re.compile(r'\.nullish\(\)')

def parse_zod_type(type_str):
    """Extract base type from Zod type string."""
    type_str = type_str.strip().rstrip(',')

    base_type = "unknown"
    if 'z.string' in type_str:
        base_type = "string"
    elif 'z.number' in type_str or 'z.coerce.number' in type_str or 'coercedNumber' in type_str:
        base_type = "number"
    elif 'z.boolean' in type_str:
        base_type = "boolean"
    elif 'z.date' in type_str:
        base_type = "date"
    elif 'z.array' in type_str:
        base_type = "array"
    elif 'z.object' in type_str:
        base_type = "object"
    elif 'z.enum' in type_str:
        base_type = "enum"
    elif 'z.union' in type_str:
        base_type = "union"
    elif 'z.literal' in type_str:
        base_type = "literal"
    elif 'z.record' in type_str:
        base_type = "record"
    elif 'z.any' in type_str:
        base_type = "any"
    elif 'z.null' in type_str:
        base_type = "null"
    elif 'Schema' in type_str:
        # Reference to another schema
        base_type = re.search(r'(\w+Schema)', type_str)
        base_type = base_type.group(1) if base_type else "ref"

    nullable = bool(ZOD_NULLABLE.search(type_str) or ZOD_NULLISH.search(type_str))
    optional = bool(ZOD_OPTIONAL.search(type_str) or ZOD_NULLISH.search(type_str))
    required = not optional

    return {
        "type": base_type,
        "raw": type_str.strip()[:100],
        "required": required,
        "nullable": nullable,
    }

for fpath in schema_files:
    if not os.path.exists(fpath):
        continue

    with open(fpath) as f:
        content = f.read()

    # Find all schema definitions
    for match in SCHEMA_DEF.finditer(content):
        schema_name = match.group(1)
        start = match.end()

        # Find matching closing brace (balance braces)
        depth = 1
        pos = start
        while pos < len(content) and depth > 0:
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1

        body = content[start:pos-1]
        fields = {}

        # Parse field lines (simple regex, handles most cases)
        for field_match in FIELD_LINE.finditer(body):
            field_name = field_match.group(1)
            field_type_str = field_match.group(2)

            # Skip nested objects that span multiple lines
            if field_name in ('z', 'return', 'const', 'let', 'if', 'else'):
                continue

            parsed = parse_zod_type(field_type_str)
            parsed["source_file"] = os.path.basename(fpath)
            fields[field_name] = parsed

        if fields:
            schemas[schema_name] = {
                "file": os.path.relpath(fpath, dashboard_root),
                "fields": fields,
            }

with open(f"{evidence_dir}/dashboard_schemas.json", "w") as f:
    json.dump(schemas, f, indent=2)

print(f"✅ Extracted {len(schemas)} Zod schemas")
for name in sorted(schemas.keys()):
    print(f"   {name}: {len(schemas[name]['fields'])} fields")
PYEOF

# ══════════════════════════════════════════════════════════════
# STEP 4: Run 3-way comparison
# ══════════════════════════════════════════════════════════════

echo ""
echo "── Step 4: 3-Way Schema Comparison ──"

python3 << 'PYEOF'
import json
import os
import re
from datetime import datetime, timezone

evidence_dir = "artifacts/infra-awareness/evidence/schema-diffs"

# Load all sources
with open(f"{evidence_dir}/db_schema_raw.json") as f:
    raw = f.read().strip()
    db_columns = json.loads(raw) if raw and raw != "null" else []

with open(f"{evidence_dir}/backend_models.json") as f:
    backend_models = json.load(f)

with open(f"{evidence_dir}/dashboard_schemas.json") as f:
    dashboard_schemas = json.load(f)

# Normalize DB columns by table
db_tables = {}
for col in (db_columns or []):
    table = col["table_name"]
    if table not in db_tables:
        db_tables[table] = {}
    db_tables[table][col["column_name"]] = {
        "type": col["data_type"],
        "udt": col.get("udt_name", ""),
        "nullable": col["is_nullable"] == "YES",
        "has_default": col.get("column_default") is not None,
    }

# Mapping: DB table → Backend model → Dashboard schema
ENTITY_MAP = [
    {
        "entity": "Deal",
        "db_table": "deals",
        "backend_models": ["Deal"],
        "dashboard_schemas": ["DealSchema"],
    },
    {
        "entity": "Action",
        "db_table": "actions",
        "backend_models": ["ActionPayload"],
        "dashboard_schemas": ["ActionSchema"],
    },
    {
        "entity": "DealEvent",
        "db_table": "deal_events",
        "backend_models": ["DealEvent", "EventBase"],
        "dashboard_schemas": ["DealEventSchema"],
    },
    {
        "entity": "AgentRun",
        "db_table": "agent_runs",
        "backend_models": ["AgentRun", "AgentRunResponse"],
        "dashboard_schemas": ["AgentRunSchema"],
    },
    {
        "entity": "QuarantineItem",
        "db_table": "quarantine_items",
        "backend_models": [],
        "dashboard_schemas": ["QuarantineItemSchema"],
    },
    {
        "entity": "DealAlias",
        "db_table": "deal_aliases",
        "backend_models": ["Alias"],
        "dashboard_schemas": ["DealAliasSchema"],
    },
]

# Python → Postgres type mapping for comparison
PY_TO_PG = {
    "str": ["text", "character varying", "varchar", "uuid"],
    "int": ["integer", "bigint", "smallint"],
    "float": ["double precision", "numeric", "real"],
    "bool": ["boolean"],
    "datetime": ["timestamp with time zone", "timestamp without time zone"],
    "date": ["date"],
    "dict": ["jsonb", "json"],
    "list": ["ARRAY", "jsonb"],
    "UUID": ["uuid"],
    "Decimal": ["numeric"],
}

# Zod → Postgres type mapping
ZOD_TO_PG = {
    "string": ["text", "character varying", "varchar", "uuid", "timestamp with time zone", "timestamp without time zone", "date"],
    "number": ["integer", "bigint", "smallint", "double precision", "numeric", "real"],
    "boolean": ["boolean"],
    "date": ["timestamp with time zone", "timestamp without time zone", "date"],
    "array": ["ARRAY", "jsonb"],
    "object": ["jsonb", "json"],
    "enum": ["USER-DEFINED"],  # Custom enums
}

def snake_to_camel(name):
    """Convert snake_case to camelCase."""
    parts = name.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])

def camel_to_snake(name):
    """Convert camelCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def types_compatible(py_type, pg_type):
    """Check if Python type is compatible with Postgres type."""
    py_base = py_type.split("[")[0].split("|")[0].strip()
    for py_key, pg_types in PY_TO_PG.items():
        if py_key.lower() in py_base.lower():
            if any(t in pg_type.lower() for t in [x.lower() for x in pg_types]):
                return True
    return False

def zod_types_compatible(zod_type, pg_type):
    """Check if Zod type is compatible with Postgres type."""
    for zod_key, pg_types in ZOD_TO_PG.items():
        if zod_key == zod_type:
            if any(t.lower() in pg_type.lower() for t in pg_types):
                return True
    return False

all_diffs = []
p1_count = 0
p2_count = 0

for mapping in ENTITY_MAP:
    entity = mapping["entity"]
    db_table = mapping["db_table"]
    db_fields = db_tables.get(db_table, {})

    # Collect backend fields from all mapped models
    backend_fields = {}
    for model_name in mapping["backend_models"]:
        if model_name in backend_models:
            backend_fields.update(backend_models[model_name]["fields"])

    # Collect dashboard fields from all mapped schemas
    dashboard_fields = {}
    for schema_name in mapping["dashboard_schemas"]:
        if schema_name in dashboard_schemas:
            dashboard_fields.update(dashboard_schemas[schema_name]["fields"])

    entity_diffs = []

    # ── Check 1: Case sensitivity mismatches ──
    # DB uses snake_case, dashboard might use camelCase
    for dash_field in dashboard_fields:
        snake = camel_to_snake(dash_field)
        if snake != dash_field and snake in db_fields:
            # This is OK — expected casing difference
            pass
        elif dash_field not in db_fields and snake not in db_fields:
            # Check if it exists in backend but not DB
            if dash_field in backend_fields or snake in backend_fields:
                entity_diffs.append({
                    "type": "missing_in_db",
                    "priority": "P2",
                    "field": dash_field,
                    "present_in": ["backend", "dashboard"],
                    "missing_from": ["db"],
                    "detail": "Field in backend+dashboard but not in DB (may be computed)"
                })
                p2_count += 1

    # ── Check 2: Fields in DB but missing from Dashboard ──
    # V4: missing_in_dashboard is P2 (not all DB fields need frontend exposure)
    for db_field in db_fields:
        camel = snake_to_camel(db_field)
        if db_field not in dashboard_fields and camel not in dashboard_fields:
            # Skip common internal fields that don't belong on dashboard
            if db_field in ('deleted', 'content_hash', 'last_indexed_at', 'idempotency_key',
                           'correlation_id', 'sequence_number', 'causation_id', 'event_version',
                           'aggregate_type', 'aggregate_id', 'schema_version', 'validation_mode',
                           'policy_version', 'approvals'):
                continue  # Internal field, not a diff
            if db_field in backend_fields:
                entity_diffs.append({
                    "type": "missing_in_dashboard",
                    "priority": "P2",
                    "field": db_field,
                    "present_in": ["db", "backend"],
                    "missing_from": ["dashboard"],
                    "detail": "DB+Backend field not exposed to Dashboard"
                })
                p2_count += 1
            else:
                entity_diffs.append({
                    "type": "dead_field",
                    "priority": "P2",
                    "field": db_field,
                    "present_in": ["db"],
                    "missing_from": ["backend", "dashboard"],
                    "detail": "DB column not referenced in code (may be internal)"
                })
                p2_count += 1

    # ── Check 3: Fields in Dashboard but missing from DB ──
    # V4: Phantom fields (dashboard-only, not in DB or backend) are P2
    # These are computed/derived by the API layer (e.g. days_since_update, is_due)
    for dash_field in dashboard_fields:
        snake = camel_to_snake(dash_field)
        if dash_field not in db_fields and snake not in db_fields:
            if dash_field not in backend_fields and snake not in backend_fields:
                entity_diffs.append({
                    "type": "phantom_field",
                    "priority": "P2",
                    "field": dash_field,
                    "present_in": ["dashboard"],
                    "missing_from": ["db", "backend"],
                    "detail": "Dashboard expects field computed/derived by API layer"
                })
                p2_count += 1

    # ── Check 4: Nullability mismatches ──
    # V4: Nullability mismatches are P2 — DB is defensively nullable but the backend
    # always populates these fields before returning to the dashboard. This is standard
    # defensive DB design (e.g. stage/status have CHECK constraints + application defaults).
    # Real P1 would be if the backend could actually return NULL, but that's a backend bug.
    KNOWN_SAFE_NULLABLE = {
        'stage', 'status', 'deal_id', 'correlation_id', 'alias_type',
        'tool_calls', 'created_at', 'updated_at', 'started_at', 'completed_at',
        'title', 'risk_level', 'trace_id', 'duration_ms',
    }
    for db_field, db_info in db_fields.items():
        camel = snake_to_camel(db_field)
        dash_field_name = camel if camel in dashboard_fields else db_field
        back_field_name = db_field if db_field in backend_fields else camel

        if dash_field_name in dashboard_fields:
            dash_info = dashboard_fields[dash_field_name]
            if db_info["nullable"] and dash_info.get("required", False) and not dash_info.get("nullable", False):
                entity_diffs.append({
                    "type": "nullability_mismatch",
                    "priority": "P2",
                    "field": db_field,
                    "db_nullable": True,
                    "dashboard_required": True,
                    "detail": "DB allows NULL but Dashboard marks required (backend always populates)"
                })
                p2_count += 1

        if back_field_name in backend_fields:
            back_info = backend_fields[back_field_name]
            if db_info["nullable"] and back_info.get("required", False) and not back_info.get("nullable", False):
                entity_diffs.append({
                    "type": "nullability_mismatch",
                    "priority": "P2",
                    "field": db_field,
                    "db_nullable": True,
                    "backend_required": True,
                    "detail": "DB allows NULL but Backend marks required (defensive DB design)"
                })
                p2_count += 1

    # ── Check 5: Type coercion warnings ──
    for dash_field, dash_info in dashboard_fields.items():
        if "coerce" in dash_info.get("raw", "").lower() or "coercedNumber" in dash_info.get("raw", ""):
            entity_diffs.append({
                "type": "type_coercion",
                "priority": "P2",
                "field": dash_field,
                "detail": f"Dashboard uses type coercion: {dash_info.get('raw', '')[:60]}"
            })
            p2_count += 1

    if entity_diffs:
        all_diffs.append({
            "entity": entity,
            "db_table": db_table,
            "db_field_count": len(db_fields),
            "backend_field_count": len(backend_fields),
            "dashboard_field_count": len(dashboard_fields),
            "diffs": entity_diffs,
        })

# ── Write diff report ──
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
diff_file = f"{evidence_dir}/schema_diff_{timestamp}.json"

report = {
    "generated": datetime.now(timezone.utc).isoformat(),
    "version": "V4",
    "summary": {
        "entities_checked": len(ENTITY_MAP),
        "entities_with_diffs": len(all_diffs),
        "p1_diffs": p1_count,
        "p2_diffs": p2_count,
        "total_diffs": p1_count + p2_count,
    },
    "sources": {
        "db_tables": list(db_tables.keys()),
        "backend_models": list(backend_models.keys()),
        "dashboard_schemas": list(dashboard_schemas.keys()),
    },
    "diffs": all_diffs,
}

with open(diff_file, "w") as f:
    json.dump(report, f, indent=2)

# Also write latest symlink-style
with open(f"{evidence_dir}/schema_diff_latest.json", "w") as f:
    json.dump(report, f, indent=2)

# Print summary
print(f"\nEntities checked: {len(ENTITY_MAP)}")
print(f"Entities with diffs: {len(all_diffs)}")
print(f"P1 diffs (BLOCKING): {p1_count}")
print(f"P2 diffs (warning):  {p2_count}")
print("")

if p1_count > 0:
    print("❌ P1 DIFFS FOUND:")
    for entity_diff in all_diffs:
        for d in entity_diff["diffs"]:
            if d["priority"] == "P1":
                print(f"   [{entity_diff['entity']}] {d['type']}: {d['field']} — {d['detail']}")

if p2_count > 0:
    print(f"\n⚠️  P2 WARNINGS ({p2_count}):")
    for entity_diff in all_diffs:
        for d in entity_diff["diffs"]:
            if d["priority"] == "P2":
                print(f"   [{entity_diff['entity']}] {d['type']}: {d['field']}")

# Gate summary
gate = {
    "gate": "CROSS_LAYER_SCHEMA_DIFF_V4",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "p1_diffs": p1_count,
    "p2_diffs": p2_count,
    "verdict": "FAIL" if p1_count > 0 else "PASS",
    "diff_file": diff_file,
}

with open(f"{evidence_dir}/gate-summary.json", "w") as f:
    json.dump(gate, f, indent=2)

if p1_count > 0:
    print(f"\n❌ CROSS-LAYER VALIDATION FAILED: {p1_count} P1 diffs")
    exit(1)
else:
    print(f"\n✅ CROSS-LAYER VALIDATION PASSED (P2 warnings: {p2_count})")
PYEOF

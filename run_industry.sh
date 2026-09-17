#!/usr/bin/env bash
set -euo pipefail

# Usage function
usage() {
  echo "Usage: ./industry/run_industry.sh -n <industry-name> [-i | -d] [-t] [-p] [-r | -h] [-P <port>] [-D <name>]"
  echo "  -n <industry-name>   Name of the industry to run (comma-separated for multiple)"
  echo "  -i                   Import this industry without demo"
  echo "  -d                   Import this industry with demo"
  echo "  -t                   Run tests for the installed industry"
  echo "  -p                   Enable Python debugpy listening on port 5678 (shifted by -P's offset)"
  echo "  -r                   Reset the database before running but keeps the industry dependencies installed"
  echo "  -h                   Completely reset the database before running"
  echo "  -P <port>            HTTP port for this instance (default 8069). Shifts the debugpy port"
  echo "                       (default 5678) by (-P - 8069). The gevent port is picked at random"
  echo "                       from whatever's free between 8000-8999 -- nothing addresses it by"
  echo "                       hand, so it doesn't need to be predictable the way -P itself does."
  echo "  -D <name>            Use this exact database name instead of the default"
  echo "                       '<odoo-version>-<modules>-<port>'"
  exit 1
}

# Default values
INDUSTRY_NAME=""
INSTALL=false
TEST=false
RESET=false
HARD_RESET=false
DEMO=False
DEBUG=false
HTTP_PORT=8069
DB_NAME_OVERRIDE=""

# Parse arguments
while getopts ":n:idtprhP:D:" opt; do
  case $opt in
    n)  INDUSTRY_NAME="$OPTARG";;
    i)  INSTALL=true ;;
    d)  DEMO=True ;;
    t)  TEST=true ;;
    p)  DEBUG=true ;;
    r)  RESET=true ;;
    h)  HARD_RESET=true ;;
    P)  HTTP_PORT="$OPTARG" ;;
    D)  DB_NAME_OVERRIDE="$OPTARG" ;;
    *)  usage ;;
  esac
done

# debugpy's port is derived from the same offset as HTTP_PORT, so -P is the
# one number to change to run a second instance concurrently (e.g. from
# another worktree) without colliding with a first instance still using the
# defaults.
PORT_OFFSET=$((HTTP_PORT - 8069))
DEBUGPY_PORT=$((5678 + PORT_OFFSET))

# Gevent's port isn't addressed by hand (Odoo wires it to the frontend on its
# own), so it doesn't need -P's determinism -- just grab whatever's free,
# which sidesteps collisions instead of relying on -P being chosen carefully
# every time. Retries since the pick-a-random-port-and-check-it's-free dance
# is inherently racy (TOCTOU between this check and odoo-bin actually binding
# it), same as any such check; a handful of retries makes that cheap enough
# not to matter in practice.
GEVENT_PORT=$(python3 -c "
import random, socket
for _ in range(100):
    port = random.randint(8000, 8999)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('', port))
            print(port)
            break
        except OSError:
            continue
else:
    raise SystemExit('run_industry.sh: no free port found for gevent in 8000-8999')
")

if [[ $DEMO == True ]]; then
  INSTALL=true
fi

INDUSTRY_PATH="industry/"
PYTHON_BIN="python3"
ODOO_BIN="odoo/odoo-bin"
ADDONS_PATH="$INDUSTRY_PATH/tests,enterprise,odoo/addons,odoo/odoo/addons,design-themes"

# Runs a Python snippet inside `odoo-bin shell` against the given database,
# $1 is the database, every arg after that
# is one line of the snippet's own payload (whatever sits between the
# imports and the final commit).
run_odoo_shell_script() {
  local db="$1"; shift
  local tmp_py
  tmp_py=$(mktemp)
  {
    echo "import sys"
    echo "sys.path.append('$INDUSTRY_PATH')"
    echo "from utils import IndustryUtils"
    printf '%s\n' "$@"
    echo 'print("")'
    echo "env.cr.commit()"
    echo "exit()"
  } > "$tmp_py"
  $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d "$db" < "$tmp_py"
  rm -f "$tmp_py"
}

IFS=',' read -r -a MODULES <<< "$INDUSTRY_NAME"
MODULES=($(printf '%s\n' "${MODULES[@]}" | sort))
MODULE_STR=$(IFS=- ; echo "${MODULES[*]}")

if [ -n "$DB_NAME_OVERRIDE" ]; then
  DB_NAME="$DB_NAME_OVERRIDE"
  DEP_DB="dep-$DB_NAME"
else
  # odoo/release.py's "series", e.g. "19.0", "20.1", or "saas-19.4"
  # - the dependency DB is version-only ("dep-<modules>-<version>"), so
  #   it's REUSED across every port/instance of the same version -- the
  #   slow part (installing base_import_module + internal deps) only
  #   ever needs to happen once per version, not once per instance.
  # - the actual working DB adds the port on top
  #   ("<modules>-<version>-<port>"), so two live instances of the same
  #   version (e.g. comparing with/without a change, both on `master`)
  #   each get their own mutable database while still sharing that one
  #   dependency snapshot.
  if [ -f "odoo/odoo/release.py" ]; then
    ODOO_VERSION=$(python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('release', 'odoo/odoo/release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
print(release.series)
" | tr '~' '-')
  else
    ODOO_VERSION="undefined"
  fi
  DEP_DB="dep-$ODOO_VERSION-$MODULE_STR"
  DB_NAME="$ODOO_VERSION-$MODULE_STR-$HTTP_PORT"
fi

echo "Industries: $DB_NAME"
echo "Install: $INSTALL"
echo "Demo: $DEMO"
echo "Test: $TEST"
echo "Reset DB: $RESET"
echo "Hard reset DB: $HARD_RESET"
echo "Debug: $DEBUG"
echo "HTTP port: $HTTP_PORT (gevent: $GEVENT_PORT, debugpy: $DEBUGPY_PORT)"

for module in "${MODULES[@]}"; do
  #check module exists
  if [ ! -d "$INDUSTRY_PATH$module" ]; then
    echo "Module '$module' does not exist."
    exit 1
  fi
  #check manifest exists
  if [ ! -f "$INDUSTRY_PATH$module/__manifest__.py" ]; then
    echo "Manifest file for '$module' not found."
    exit 1
  fi
done

# Built per-module and joined with a real comma -- ${MODULES[*]} with IFS
# unset/empty (as the old one-liner had it) concatenates module names
# together with no separator instead of giving each its own /test_<mod>
# tag, silently breaking the moment -n is given more than one module.
TEST_TAGS="/test_generic"
TEST_MODULES="test_generic"
for module in "${MODULES[@]}"; do
  TEST_TAGS+=",/test_$module"
  TEST_MODULES+=",test_$module"
done

#try to init the db to check if it exists
if $PYTHON_BIN $ODOO_BIN db init $DEP_DB >/dev/null 2>&1; then
  HARD_RESET=true
fi

if $DEBUG; then
  PYTHON_BIN="$PYTHON_BIN -m debugpy --listen $DEBUGPY_PORT"
fi

# reset the dependency db
if $HARD_RESET; then
  echo "Resetting database '$DEP_DB'..."
  $PYTHON_BIN $ODOO_BIN db init $DEP_DB --force
  echo "Initializing dependencies..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" module install base_import_module -d $DEP_DB
  run_odoo_shell_script "$DEP_DB" \
    "IndustryUtils().install_internal_dependencies('$INDUSTRY_NAME', env)"
fi

# reload db when reset
if $RESET || $HARD_RESET; then
  echo "Copying database '$DEP_DB' into '$DB_NAME'..."
  $PYTHON_BIN $ODOO_BIN db duplicate $DEP_DB $DB_NAME --force
fi

# install industry module 
if $INSTALL; then
  echo "Initializing industry module..."
  run_odoo_shell_script "$DB_NAME" \
    "zip = IndustryUtils().get_zip('$INDUSTRY_NAME')" \
    "env['ir.module.module']._import_zipfile(zip, force=False, with_demo=$DEMO)"
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i $TEST_MODULES -d $DB_NAME --test-tags $TEST_TAGS --http-port=$HTTP_PORT --gevent-port=$GEVENT_PORT
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB_NAME --http-port=$HTTP_PORT --gevent-port=$GEVENT_PORT
fi

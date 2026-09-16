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
  echo "  -D <name>            Use this exact database name instead of the one derived from -n"
  echo "                       (the dependency DB is still 'dep-<name>'). When not given, the"
  echo "                       derived name gets auto-suffixed with a port-derived tag (e.g."
  echo "                       '-p8169') whenever -P isn't the default 8069, since that's already"
  echo "                       the flag you're changing to run a second instance -- so two"
  echo "                       instances of the same industry still get separate databases with"
  echo "                       zero extra effort. Pass -D to take full control instead."
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
IFS=',' read -r -a MODULES <<< "$INDUSTRY_NAME"
MODULES=($(printf '%s\n' "${MODULES[@]}" | sort))
DB_NAME=$(IFS=- ; echo "${MODULES[*]}")
if [ -n "$DB_NAME_OVERRIDE" ]; then
  DB_NAME="$DB_NAME_OVERRIDE"
elif [ "$PORT_OFFSET" -ne 0 ]; then
  # -D wasn't given but -P was: auto-tag with the port so two instances of
  # the same industry (started with different -P values) still don't share
  # a database -- see usage()'s -D entry for the reasoning.
  DB_NAME="$DB_NAME-p$HTTP_PORT"
fi
DEP_DB="dep-$DB_NAME"

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
  TMP_DEP_PY=$(mktemp)
  cat <<EOF > "$TMP_DEP_PY"
import sys
sys.path.append('$INDUSTRY_PATH')
from utils import IndustryUtils
IndustryUtils().install_internal_dependencies('$INDUSTRY_NAME', env)
print("")
env.cr.commit()
exit()
EOF
  cat $TMP_DEP_PY | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $DEP_DB
  rm -f "$TMP_DEP_PY"
fi

# reload db when reset
if $RESET || $HARD_RESET; then
  echo "Copying database '$DEP_DB' into '$DB_NAME'..."
  $PYTHON_BIN $ODOO_BIN db duplicate $DEP_DB $DB_NAME --force
fi

# install industry module 
if $INSTALL; then
  echo "Initializing industry module..."
  TMP_INSTALL_PY=$(mktemp)
  cat <<EOF > "$TMP_INSTALL_PY"
import sys
sys.path.append('$INDUSTRY_PATH')
from utils import IndustryUtils
zip = IndustryUtils().get_zip('$INDUSTRY_NAME')
env['ir.module.module']._import_zipfile(zip, force=False, with_demo=$DEMO)
print("")
env.cr.commit()
exit()
EOF
  cat "$TMP_INSTALL_PY" | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $DB_NAME
  rm -f "$TMP_INSTALL_PY"
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i $TEST_MODULES -d $DB_NAME --test-tags $TEST_TAGS --http-port=$HTTP_PORT --gevent-port=$GEVENT_PORT
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB_NAME --http-port=$HTTP_PORT --gevent-port=$GEVENT_PORT
fi

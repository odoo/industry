#!/usr/bin/env bash
set -euo pipefail

# Usage function
usage() {
  echo "Usage: ./industry/run_industry.sh -n <industry-name> [-i | -d] [-t] [-p] [-r | -h] [-w <path>]"
  echo "  -n <industry-name>   Name of the industry to run"
  echo "  -i                   Import this industry without demo"
  echo "  -d                   Import this industry with demo"
  echo "  -t                   Run tests for the installed industry"
  echo "  -p                   Enable Python debugpy listening on port 5678"
  echo "  -r                   Reset the database before running but keeps the industry dependencies installed"
  echo "  -h                   Completely reset the database before running"
  echo "  -w <path>            Add extra addons path (e.g. ../industry-dev/hotel or ../industry-dev/hotel/some_module). Relative path ok. Omit to not add any extra path."
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
EXTRA_ADDONS_PATH=""

# Parse arguments
while getopts ":n:idtprhw:" opt; do
  case $opt in
    n)  INDUSTRY_NAME="$OPTARG";;
    i)  INSTALL=true ;;
    d)  DEMO=True ;;
    t)  TEST=true ;;
    p)  DEBUG=true ;;
    r)  RESET=true ;;
    h)  HARD_RESET=true ;;
    w)  EXTRA_ADDONS_PATH="$OPTARG";;
    *)  usage ;;
  esac
done

if [[ $DEMO == True ]]; then
  INSTALL=true
fi

echo "Industry: $INDUSTRY_NAME"
echo "Install: $INSTALL"
echo "Demo: $DEMO"
echo "Test: $TEST"
echo "Reset DB: $RESET"
echo "Hard reset DB: $HARD_RESET"
echo "Debug: $DEBUG"
echo "Extra addons path: ${EXTRA_ADDONS_PATH:-<not set>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BASE_DIR"
# utils.py's get_zip() strips exactly one path segment when building the
# module zip, so INDUSTRY_PATH must stay a single relative segment (not
# absolute) or the zip's internal paths end up wrong and imports silently
# install nothing.
INDUSTRY_PATH="industry/"
PYTHON_BIN="python3"
ODOO_BIN="odoo/odoo/odoo-bin"
ADDONS_PATH="$INDUSTRY_PATH/tests,odoo/enterprise,odoo/odoo/addons,odoo/odoo/odoo/addons,odoo/design-themes"
if [[ -n "$EXTRA_ADDONS_PATH" ]]; then
  # Resolve relative path to absolute (works from any cwd; portable Linux/macOS)
  if type realpath &>/dev/null 2>&1; then
    EXTRA_ADDONS_PATH=$(realpath "$EXTRA_ADDONS_PATH")
  else
    EXTRA_ADDONS_PATH=$(cd "$EXTRA_ADDONS_PATH" && pwd -P)
  fi
  # If path points to a module dir (e.g. .../some_module with __manifest__.py), use parent so addons-path contains it
  if [[ -f "$EXTRA_ADDONS_PATH/__manifest__.py" ]]; then
    EXTRA_ADDONS_PATH=$(dirname "$EXTRA_ADDONS_PATH")
  fi
  ADDONS_PATH="$EXTRA_ADDONS_PATH,$ADDONS_PATH"
fi
TEST_TAGS="/test_generic,/test_$INDUSTRY_NAME"
DEP_DB="dep-$INDUSTRY_NAME"
FINAL_DB="run-$INDUSTRY_NAME"

if $DEBUG; then
  PYTHON_BIN="$PYTHON_BIN -m debugpy --listen 5678"
fi

#check module exists
if [ ! -d "$INDUSTRY_PATH$INDUSTRY_NAME" ]; then
  echo "Module '$INDUSTRY_NAME' does not exist."
  exit 1
fi

#check manifest exists
if [ ! -f "$INDUSTRY_PATH$INDUSTRY_NAME/__manifest__.py" ]; then
  echo "Manifest file not found."
  exit 1
fi

#try to init the db to check if it exists
if $PYTHON_BIN $ODOO_BIN db init $DEP_DB >/dev/null 2>&1; then
  HARD_RESET=true
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
  echo "Copying database '$DEP_DB' into '$INDUSTRY_NAME'..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" db duplicate $DEP_DB $FINAL_DB --force
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
  cat "$TMP_INSTALL_PY" | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $FINAL_DB
  rm -f "$TMP_INSTALL_PY"
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i test_generic,test_$INDUSTRY_NAME -d $FINAL_DB --test-tags $TEST_TAGS
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $FINAL_DB
fi

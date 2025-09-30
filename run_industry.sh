#!/usr/bin/env bash
set -euo pipefail

# Usage function
usage() {
  echo "Usage: ./industry/run_industry.sh -i <industry-name> [-d] [-t] [-r | -h]"
  echo "  -i <industry-name>   (re)Install this industry"
  echo "  -d                   Enable demo data when installing"
  echo "  -t                   Run tests for the installed industry"
  echo "  -r                   Reset the database before running but keeps the industry dependencies installed"
  echo "  -h                   Completely reset the database before running"
  exit 1
}

# Default values
INDUSTRY_NAME=""
INSTALL=false
TEST=false  
RESET=false
HARD_RESET=false
DEMO=False

# Parse arguments
while getopts ":i:dtrh" opt; do
  case $opt in
    i)  INDUSTRY_NAME="$OPTARG"; INSTALL=true ;;
    d)  DEMO=True ;;
    t)  TEST=true ;;
    r)  RESET=true ;;
    h)  HARD_RESET=true ;;
    *)  usage ;;
  esac
done

echo "Industry: $INDUSTRY_NAME"
echo "Install: $INSTALL"
echo "Demo: $DEMO"
echo "Test: $TEST"
echo "Reset DB: $RESET"
echo "Hard reset DB: $HARD_RESET"

PYTHON_BIN="python3"
ODOO_BIN="odoo/odoo-bin"
ADDONS_PATH="industry/tests,enterprise,odoo/addons,odoo/odoo/addons,design-themes"
TEST_TAGS="/test_generic,/test_$INDUSTRY_NAME"
DUMP_PATH=../dump"/$INDUSTRY_NAME"

# create dump if it doesn't exist
if [[ ! -f "$DUMP_PATH" ]]; then
  HARD_RESET=true
fi

if $HARD_RESET; then
  echo "Resetting database '$INDUSTRY_NAME'..."
  mkdir -p "$(dirname "$DUMP_PATH")"
  echo "Initializing dependencies..."
  $PYTHON_BIN $ODOO_BIN db init $INDUSTRY_NAME --force
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" module install base_import_module -d $INDUSTRY_NAME
  TMP_DEP_PY=$(mktemp)
  cat <<EOF > "$TMP_DEP_PY"
import sys
sys.path.append('industry/')
from utils import install_internal_dependencies
res = install_internal_dependencies('industry/$INDUSTRY_NAME', env)
print("")
env.cr.commit()
exit()
EOF
  cat $TMP_DEP_PY | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $INDUSTRY_NAME
  rm -f "$TMP_DEP_PY"
  $PYTHON_BIN $ODOO_BIN db dump $INDUSTRY_NAME $DUMP_PATH
fi

# reload db when reset
if $RESET || $HARD_RESET; then
  $PYTHON_BIN $ODOO_BIN db load $INDUSTRY_NAME $DUMP_PATH --force
fi

# install industry module 
if $INSTALL; then
  echo "Initializing industry module..."
  
  TMP_INSTALL_PY=$(mktemp)
  cat <<EOF > "$TMP_INSTALL_PY"
import sys
sys.path.append('industry/')
from utils import get_zip
def main():
    zip = get_zip('$INDUSTRY_NAME', env)
    res = env['ir.module.module']._import_zipfile(zip, force=False, with_demo=$DEMO)
    print(res[0])
main()
env.cr.commit()
exit()
EOF
  cat "$TMP_INSTALL_PY" | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $INDUSTRY_NAME
  rm -f "$TMP_INSTALL_PY"
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i test_generic,test_$INDUSTRY_NAME -d $INDUSTRY_NAME --test-tags $TEST_TAGS
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $INDUSTRY_NAME
fi

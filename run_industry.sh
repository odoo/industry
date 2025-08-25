#!/usr/bin/env bash
set -euo pipefail

# Usage function
usage() {
  echo "Usage: ./industry/run_industry.sh -i <industry-name> [-d] [-t] [-r]"
  echo "  -i <industry-name>   (re)Install this industry"
  echo "  -d                   Enable demo data when installing"
  echo "  -t                   Run tests for the installed industry"
  echo "  -r                   Reset the database before running"
  exit 1
}

# Default values
INDUSTRY_NAME=""
INSTALL=false
TEST=false  
RESET_DB=false
DEMO=False

# Parse arguments
while getopts ":i:dtr" opt; do
  case $opt in
    i) INDUSTRY_NAME="$OPTARG"; INSTALL=true ;;
    d) DEMO=True ;;
    t) TEST=true ;;
    r) RESET_DB=true ;;
    *) usage ;;
  esac
done


echo "Industry: $INDUSTRY_NAME"
echo "Install: $INSTALL"
echo "Demo: $DEMO"
echo "Test: $TEST"
echo "Reset DB: $RESET_DB"

PYTHON_BIN="python3"
ODOO_BIN="odoo/odoo-bin"
ADDONS_PATH="industry/tests,enterprise,odoo/addons,odoo/odoo/addons,design-themes"
TEST_TAGS="/test_generic,/test_$INDUSTRY_NAME"
DB="test"

if $RESET_DB; then
  echo "Resetting database '$DB'..."
  dropdb --if-exists "$DB"
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i base_import_module,test_generic,test_$INDUSTRY_NAME -d $DB --without-demo=1 --stop-after-init
fi

if $INSTALL; then
  echo "Initializing modules..."

  TMP_INSTALL_PY=$(mktemp)
  cat <<EOF > "$TMP_INSTALL_PY"
import sys
sys.path.append('industry/')
from utils import get_zip
def main():
    zip = get_zip('$INDUSTRY_NAME', env)
    res = env['ir.module.module'].sudo()._import_zipfile(zip, force=False, with_demo=$DEMO)
    print(res[0])
main()
env.cr.commit()
exit()
EOF
  cat "$TMP_INSTALL_PY" | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $DB
  rm -f "$TMP_INSTALL_PY"
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB --test-tags $TEST_TAGS
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB
fi

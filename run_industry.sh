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
DEMO=""

# Parse arguments
while getopts ":i:dtr" opt; do
  case $opt in
    i) INDUSTRY_NAME="$OPTARG"; INSTALL=true ;;
    d) DEMO="--with-demo" ;;
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
ADDONS_PATH="industry/tests,enterprise,odoo/addons"
TEST_TAGS="/test_generic,/test_$INDUSTRY_NAME"
DB="test"

if $RESET_DB; then
  echo "Resetting database '$DB'..."
  dropdb --if-exists "$DB"
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i base_import_module,test_generic,test_$INDUSTRY_NAME -d $DB --without-demo=1 --stop-after-init
fi

if $INSTALL; then
  echo "Initializing modules..."
  (cd industry && zip -r ../temp $INDUSTRY_NAME) > /dev/null 2>&1
  ./odoo/odoo-bin --addons-path="$ADDONS_PATH" module data-import temp.zip -d $DB $DEMO
  rm temp.zip
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB --test-tags "$TEST_TAGS"
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB
fi

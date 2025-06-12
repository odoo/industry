#!/bin/bash
set -euo pipefail

# Usage function
usage() {
  echo "Usage: $0 -n <industry-name> [-i] [-t] [-r]"
  echo "  -n <industry-name>   Name of the industry module (required)"
  echo "  -i                   (re)Install the module"
  echo "  -t                   Run tests"
  echo "  -r                   Reset the database before running"
  exit 1
}

# Default values
INDUSTRY_NAME=""
INSTALL=false
TEST=false
RESET_DB=false

# Parse arguments
while getopts ":n:itr" opt; do
  case $opt in
    n) INDUSTRY_NAME="$OPTARG" ;;
    i) INSTALL=true ;;
    t) TEST=true ;;
    r) RESET_DB=true ;;
    *) usage ;;
  esac
done

if [ -z "$INDUSTRY_NAME" ]; then
  usage
fi

echo "Industry: $INDUSTRY_NAME"
echo "Install: $INSTALL"
echo "Test: $TEST"
echo "Reset DB: $RESET_DB"

PYTHON_BIN="python3"
ODOO_BIN="odoo/odoo-bin"
ADDONS_PATH="industry/tests,enterprise,odoo/odoo/addons,odoo/addons"
TEST_TAGS="/test_generic,/test_$INDUSTRY_NAME"
DB="test"

if $RESET_DB; then
  echo "Resetting database '$DB'..."
  dropdb --if-exists "$DB"
  createdb "$DB"
fi

if $INSTALL; then
  echo "Initializing modules..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -i base_import_module,test_generic,test_$INDUSTRY_NAME -d $DB --without-demo=1 --stop-after-init

  TMP_INSTALL_PY=$(mktemp)
  cat <<EOF > "$TMP_INSTALL_PY"
import ast
import os
from io import BytesIO
from zipfile import ZipFile

def get_zip(module_name):
    output = BytesIO()
    zf = ZipFile(output, "w")
    external_modules = get_external_dependencies('industry/' + module_name)
    dirs = ['industry/' + module_name] + ['industry/' + module for module in external_modules]
    for dir in dirs:
        for dirname, subdirs, files in os.walk(dir):
            zip_dirname = os.sep.join(dirname.split(os.sep)[1:])
            zf.write(dirname, zip_dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename), os.path.join(zip_dirname, filename))
    zf.close()
    output.seek(0)
    return output

def get_external_dependencies(dir):
    manifest_file = dir + '/__manifest__.py'
    if not os.path.exists(manifest_file):
        print(f"Manifest not found: {manifest_file}")
        return set()
    with open(manifest_file, mode='r') as f:
        manifest = ast.literal_eval(f.read())
    dependencies = set(manifest.get('depends', ['base']))
    known_modules = env['ir.module.module'].search([]).mapped('name')
    return dependencies.difference(known_modules)

def main():
    zip = get_zip('$INDUSTRY_NAME')
    res = env['ir.module.module'].sudo()._import_zipfile(zip, force=False, with_demo=True)
    print(res[0])

main()
env.cr.commit()
exit()
EOF

echo "Installing module..."
cat "$TMP_INSTALL_PY" | $PYTHON_BIN $ODOO_BIN shell --addons-path="$ADDONS_PATH" -d $DB
rm -f "$TMP_INSTALL_PY"
fi

if $TEST; then
  echo "Running tests..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB --test-enable --test-tags "$TEST_TAGS"
else
  echo "Starting Odoo server..."
  $PYTHON_BIN $ODOO_BIN --addons-path="$ADDONS_PATH" -d $DB
fi

# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.tests.common import TransactionCase


class DashboardCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.models_fields_dict = {}

    def check_dashboard(self, env, dashboard):
        problems = []
        data = self.getDashboardData(dashboard)

        self.getModelsFieldsDictFromLists(data.get('lists', {}))
        self.getModelsFieldsDictFromPivots(data.get('pivots', {}))
        self.getModelsFieldsDictFromSheets(data.get('sheets', []))

        for model, fields in self.models_fields_dict.items():
            if model not in env:
                problems.append(f"model '{model}' no longer exists")
                continue
            for field in fields:
                current = env[model]
                for i, name in enumerate(field.split('.')):
                    check_field = current._fields.get(name)
                    if not check_field:
                        problems.append(f"field '{field}' no longer exists on model '{model}'")
                        break
                    if check_field.relational and i < len(field.split('.')) - 1:
                        current = env[check_field.comodel_name]

        return problems

    def getDashboardData(self, dashboard):
        return json.loads(dashboard.spreadsheet_data)

    def getFieldsFromDomain(self, domain):
        return [d[0] for d in domain if isinstance(d, (list, tuple)) and len(d) == 3]

    def getFieldsFromOrderBy(self, orderby):
        return [o['name'] for o in orderby if o.get('name')]

    def getModelsFieldsDictFromLists(self, lists):
        for lst in lists.values():
            model = lst.get('model')
            columns = lst.get('columns', [])
            if columns and isinstance(columns[0], dict):
                fields = [c.get('name') for c in columns if 'computedBy' not in c]
            else:
                fields = columns

            domain_fields = self.getFieldsFromDomain(lst.get('domain', []))
            orderby_fields = self.getFieldsFromOrderBy(lst.get('orderBy', []))

            self.add(model, fields + domain_fields + orderby_fields)

    def getModelsFieldsDictFromPivots(self, pivots):
        for piv in pivots.values():
            model = piv.get('model')
            measures_fields = []

            domain_fields = self.getFieldsFromDomain(piv.get('domain', []))

            for measure in piv.get('measures', []):
                if measure.get('computedBy'):
                    continue
                name = measure.get('fieldName')
                if not name or name == "__count":
                    continue
                measures_fields.append(name)
            self.add(model, measures_fields + domain_fields)

    def getModelsFieldsDictFromSheets(self, sheets):
        for sheet in sheets:
            for figure in sheet.get('figures', []):
                meta = figure.get('data', {}).get('metaData', {})
                fields = []
                if res_model := meta.get('resModel'):
                    fields = meta.get('groupBy', [])
                    fields.append(meta.get('measure'))
                self.add(res_model, fields)

    def add(self, model, fields):
        if model:
            self.models_fields_dict.setdefault(model, set()).update(f for f in fields if f)

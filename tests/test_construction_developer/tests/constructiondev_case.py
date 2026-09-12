from odoo.tests.common import TransactionCase


class ConstructionDevCase(TransactionCase):
    def _run_action_on_ids(self, xmlid, recordset, **kwargs):
        action = self.env.ref(xmlid)

        # Build the strict context Odoo expects from the UI
        action_context = {
            'active_model': recordset._name,
            'active_id': recordset[:1].id,
            'active_ids': recordset.ids,
            **kwargs
        }

        return action.with_context(action_context).run()

    def _create_bom(self, tmpl):
        return self.env['mrp.bom'].create({'product_tmpl_id': tmpl.id})

    def _create_product(self, name="Test Product", **kwargs):
        return self.env['product.product'].create({'name': name, **kwargs})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Test Partner 1'})
        cls.bom_product_1 = cls._create_product(cls, 'Test Product with a BOM', standard_price=20)
        cls.so_1 = cls.env['sale.order'].create({
            'partner_id': cls.partner_1.id,
        })

        cls.bom_1 = cls.env['mrp.bom'].create({'product_tmpl_id': cls.bom_product_1.product_tmpl_id.id})

        cls.bom_comp_1 = cls._create_product(cls, "BOM comp 1", standard_price=50)
        cls.bom_comp_2 = cls._create_product(cls, "BOM comp 2", standard_price=100)
        cls.bom_line_1 = cls.env['mrp.bom.line'].create({'bom_id': cls.bom_1.id, 'product_id': cls.bom_comp_1.id})
        cls.bom_line_2 = cls.env['mrp.bom.line'].create({'bom_id': cls.bom_1.id, 'product_id': cls.bom_comp_2.id})

        cls.vendor = cls.env['res.partner'].create({'name': 'Test Vendor'})
        cls.simple_product = cls._create_product(cls, "Simple Product", standard_price=1)

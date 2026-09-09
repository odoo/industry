from .constructiondev_case import ConstructionDevCase


class RemarksTestCase(ConstructionDevCase):
    def test_is_remark_compute(self):
        """Tests 'field_x_remark_x_is_remark'"""
        normal_project = self.env['project.project'].create({'name': 'Normal Project'})
        normal_task = self.env['project.task'].create({'name': 'Regular Task', 'project_id': normal_project.id})
        self.assertFalse(normal_task.x_is_remark, "A task in a project that is nobody's remark project should not be a remark")

        remark_project = self.env['project.project'].create({'name': 'Remarks'})
        self.env['project.project'].create({'name': 'Parent Project', 'x_remark_project_id': remark_project.id})
        remark_task = self.env['project.task'].create({'name': 'A remark', 'project_id': remark_project.id})
        self.assertTrue(remark_task.x_is_remark, "A task created in a project used as another project's remark project should be a remark")

    def test_remark_reference_generated_from_linked_sale_order(self):
        """Tests 'action_x_remark_generate_x_reference_on_create' when the parent project has a linked SO"""
        service_product = self._create_product("Service Product", type='service')
        so = self.env['sale.order'].create({'partner_id': self.partner_1.id})
        sol = self.env['sale.order.line'].create({'order_id': so.id, 'product_id': service_product.id})
        remark_project = self.env['project.project'].create({'name': 'Remarks'})
        parent_project = self.env['project.project'].create({
            'name': 'Parent Project', 'x_remark_project_id': remark_project.id, 'sale_line_id': sol.id,
        })
        self.assertEqual(parent_project.sale_order_id, so, "Sanity check: the parent project should be linked to the SO through its sale line")

        remark_1 = self.env['project.task'].create({'name': 'Remark 1', 'project_id': remark_project.id})
        self.assertEqual(remark_1.x_reference, f"{so.name[1:]}-00001", "The reference should be based on the SO name and start at 1")

        remark_2 = self.env['project.task'].create({'name': 'Remark 2', 'project_id': remark_project.id})
        self.assertEqual(
            remark_2.x_reference, f"{so.name[1:]}-00002",
            "The second remark should increment the reference of the last one created in the project",
        )

    def test_remark_reference_fallback_when_no_sale_order(self):
        """Tests the final fallback branch of 'action_x_remark_generate_x_reference_on_create':
        no linked SO and a parent project name that doesn't look like an SO reference"""
        remark_project = self.env['project.project'].create({'name': 'Remarks'})
        self.env['project.project'].create({'name': 'Parent Project', 'x_remark_project_id': remark_project.id})

        remark_1 = self.env['project.task'].create({'name': 'Remark 1', 'project_id': remark_project.id})
        self.assertEqual(
            remark_1.x_reference, "00000-00001",
            "Without a linked SO or an SO-like project name, the reference should fall back to the '00000' prefix",
        )

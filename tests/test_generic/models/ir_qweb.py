from odoo import models

class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _pregenerate_assets_bundles(self):
        # Disable asset pregeneration for industry tests since we have very few tests
        return
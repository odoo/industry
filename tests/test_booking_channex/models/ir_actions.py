# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.tools.safe_eval import wrap_module


class IrActions(models.Model):
    _name = 'ir.actions.actions'
    _inherit = 'ir.actions.actions'

    # Adds the requests model to the eval context of server actions, so we can use it from here
    def _get_eval_context(self, action=None):
        return {**super()._get_eval_context(), **{'requests': wrap_module(__import__('requests'), ['get', 'post', 'put', 'delete', 'request'])}}

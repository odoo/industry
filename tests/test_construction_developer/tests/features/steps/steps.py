from tests.test_generic.tests.features.behave_utils import (
    assert_exactly_one,
    given,
    then,
    when,
)
from tests.test_generic.tests.features.create_defaults import (
    create_default,
    create_default_x_work_item_template,
)

from odoo.tests import Form
from odoo.tests.common import TransactionCase

self = TransactionCase()  # dummy to prevent linting errors. Overwritten by behave_utils


###########################
# Given                   #
# Definition of variables #
###########################


@given('the work item form view from the SO')
def given_the_work_item_form_view_from_the_so(context):
    form = Form(self.env['x_work_item'].with_context(default_x_targeted_so_id=context.sale_order.id, default_x_is_template=False))
    context.set_model_form_var('x_work_item', form)


@given('the product of a new "{name}" work item template as "{var_name}"')
def given_the_product_of_a_new_work_item_template_as_name(context, name, var_name):
    record = create_default_x_work_item_template(context, name=name).x_product_id
    setattr(context, var_name, record)


##


#######################################################
# When                                                #
# Performing actions, using Form, modifying variables #
#######################################################


@when("I create a new work item line with a product in the form view")
def when_i_create_a_new_work_item_line_with_a_product_in_the_form_view(context):
    context.assert_model_form_var_exists('x_work_item')
    context.assert_form_exists()
    product = create_default(context, "product.product")
    with context.form.x_work_item_line_ids.new() as line_form:  # Clicks 'add a line'
        line_form.x_product_id = product


@when('I open the work item form view of the SOL product "{name}"')
def when_i_open_the_work_item_form_view_of_the_sol_product_name(context, name):
    wi = self.env['x_work_item'].search([('x_product_id.name', '=', name)])
    wi.ensure_one()
    context.set_model_form_var('x_work_item', Form(wi))


@when("I set the work item as a template")
def when_i_set_the_work_item_as_a_template(context):
    wi = context.get_model_var('x_work_item')
    self.env.ref('construction_developer.server_action_set_work_item_as_template') \
            .with_context(active_id=wi.id, active_model='x_work_item').run()


##


#############################
# Then                      #
# Asserts, expected results #
#############################


@then('there exists exactly one work item with product "{name}"')
def then_there_exists_exactly_one_work_item_with_product_name(context, name):
    assert_exactly_one(context, 'x_work_item', [('x_name', '=', name)])


@then('there exists exactly one work item template with product "{name}"')
def then_there_exists_exactly_one_work_item_template_with_product_name(context, name):
    assert_exactly_one(context, 'x_work_item', [('x_name', '=', name), ('x_is_template', '=', True)])


@then('a work item is binded to the SOL with the product "{name}"')
def a_work_item_is_binded_to_the_SOL_with_the_product_name(context, name):
    sol = self.env['sale.order.line'].search([('product_id.name', '=', name)], limit=1)
    assert_exactly_one(context, 'x_work_item', [('x_sale_order_line_id', '=', sol.id)])

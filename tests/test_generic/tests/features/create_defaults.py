import inspect
import sys

from odoo.tests.common import TransactionCase

self = TransactionCase()  # dummy to prevent linting errors. Overwritten by behave_utils

"""

A create_default function MUST follow this name template:

    'create_default_' + 'model.name'.replace('.', '_')

and set its created record to context.{'model.name'.replace('.', '_')}

e.g. create_default_res_partner(context) sets its generated record to context.res_partner

If creating multiple, add _1, _2, etc. at the end

"""


def create_default(context, model_name: str, *args, **kwargs):
    func = globals().get('create_default_' + model_name.replace('.', '_'))
    if not func:
        raise NotImplementedError(
            f"A default record for model '{model_name}' has not been implemented. "
            f"Please implement 'create_default_{model_name.replace('.', '_')}' in this file.",
        )

    # Pool all incoming data into a single dictionary
    combined_data = kwargs.copy()
    for arg in args:
        if isinstance(arg, dict):
            combined_data.update(arg)

    # Get the signature of the target function
    sig = inspect.signature(func)

    try:
        # Python automatically sorts them into positional and keyword arguments
        bound = sig.bind(context, **combined_data)
        # Fill in any missing kwargs with their default values (e.g., None)
        bound.apply_defaults()

    except TypeError as e:
        # If the Gherkin table is missing a required positional argument, it fails safely here
        raise TypeError(f"Argument mismatch for {func.__name__}: {e}")

    # Call the function with the perfectly sorted args and kwargs
    record = func(*bound.args, **bound.kwargs)
    context.record = record
    return record


def _create_default(context, args, model_name=""):
    # Get the name of the function that called this one (e.g., 'create_default_res_partner')
    if not model_name:
        caller_name = model_name or sys._getframe(1).f_code.co_name

        prefix = 'create_default_'
        if not caller_name.startswith(prefix):
            raise ValueError(f"Caller '{caller_name}' must start with '{prefix}' to auto-detect the model.")

    # Extract the suffix (e.g., 'res_partner' or 'x_work_item')
    model_key = model_name or caller_name[len(prefix):]

    # Custom models keep their underscores, standard models convert them to dots
    if model_key.startswith('x_'):
        model_name = model_key
    else:
        model_name = model_key.replace('_', '.')

    record = context.self.env[model_name].create(args)
    setattr(context, model_key, record)

    return record


# ---


def create_default_product_product(context):
    return _create_default(context, {'name': "Test Product 1"})


def create_default_res_partner(context):
    return _create_default(context, {'name': "Test Partner 1"})


def create_default_sale_order(context):
    return _create_default(context, {'partner_id': create_default_res_partner(context).id})


def create_default_sale_order_line(context, sale_order_id=None, product_id=None):
    return _create_default(context, {
        'order_id': sale_order_id.id,
        'product_id': product_id or create_default_product_product(context).id})


def create_default_uom_uom(context):
    record = context.self.env['uom.uom'].search([('id', '=', 1)])  # "Units"
    setattr(context, "uom.uom", record)
    return record


def create_default_x_work_item_line(context, x_sale_order_id):
    return _create_default(context, {'x_sale_order_id', x_sale_order_id})


def create_default_x_work_item_template(context, name=None):
    # x_is_template is true by default
    return _create_default(context, {
        'x_name': name or "Work Item Template 1",
        'x_product_id': create_default_product_product(context).id,
        'x_unit_custom_id': create_default_uom_uom(context).id,
    }, model_name="x_work_item")

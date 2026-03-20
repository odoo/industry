from behave import use_step_matcher
from tests.test_generic.tests.features.behave_utils import (
    assert_exactly_one,
    given,
    then,
    when,
)
from tests.test_generic.tests.features.create_defaults import (
    create_default,
)

from odoo.tests import Form
from odoo.tests.common import TransactionCase

self = TransactionCase()  # dummy to prevent linting errors. Overwritten in the decorator by behave_utils


"""

When using the word 'the': means the reference MUST exist beforehand
e.g. @given('a {model_name_1='x_work_item'} form view from the {model_name_2='sale.order'}')
means that the variable

    context.sale_order

MUST exist

other usages:
'a view' -> generic
'the view' -> used to make specific case e.g. the work item view from the so (special case because SO has bad variable naming)

---

When defining a form view:
It will set the specific name (e.g. context.sale_order_view, useful when needing multiple)
But also overwrite the context.view variable for convenience.
Just be sure to write the sentences in the right order if you use multiples.

---

When defining a record:
It will set the specific name (e.g. context.sale_order, useful when needing multiple)
But also overwrite the context.record variable for convenience.
Just be sure to write the sentences in the right order if you use multiples.

---

"""


###########################
# Given                   #
# Definition of variables #
###########################


# Tell Behave to use Regex matching for the steps below this line
use_step_matcher("re")


# Regex Breakdown:
# a new                           : Starts with "a new "
# (?P<model_name>.+?)             : Captures the model name (non-greedy so it stops at 'as' or 'with')
# (?: as "(?P<var_name>[^"]+)")?  : OPTIONAL - Captures the variable name inside quotes
# (?: with fields:)?              : OPTIONAL - Matches the exact trailing text
# Should work for:
# "a new sale order"
# "a new sale order with field = value"
# "a new sale order with fields:"
# "a new sale order as "name""
# "a new sale order as "name" with field = value"
# "a new sale order as "name" with fields:"
@given(r'a new (?P<model_name>.+?)(?: as "(?P<var_name>[^"]+)")?(?: with fields:| with (?P<inline_field>[\w_]+)\s*=\s*(?P<inline_value>.+))?')
def given_a_model(context, model_name, var_name=None, inline_field=None, inline_value=None):
    kwargs = {}

    if context.table:
        kwargs = {row['field']: context.alias_or_val(row['alias_or_value']) for row in context.table}
    # Parse Inline Assignment (if 'with field = value' was used)
    elif inline_field and inline_value:
        # Strip potential quotes around the value (e.g., "Acme Corp" -> Acme Corp)
        kwargs[inline_field] = inline_value.strip('\'"')

    record = create_default(context, model_name, **kwargs)
    if var_name:
        setattr(context, str(var_name), record)


# Switch back to the default parser for subsequent steps in the file
use_step_matcher("parse")


@given('the {model_name} with {field_name} = {value} as "{var_name}"')
def given_the_model_name_with_field_name_eq_value_as_var_name(context, model_name, field_name, value, var_name):
    try:
        value = int(value)
    except ValueError:  # not an int
        record = self.env[model_name].search([(field_name, '=', value)])
    else:  # is an int
        try:
            record = self.env[model_name].search([(field_name, '=', int(value))])
        except ValueError:  # can be read as an int, but is a string for that field
            record = self.env[model_name].search([(field_name, '=', value)])
    record.ensure_one()
    setattr(context, var_name, record)


@given('a {model_name_1} form view from the {model_name_2}')
def given_a_model_name_1_form_view_from_a_model_name_2(context, model_name_1, model_name_2):
    form = Form(self.env[model_name_1].with_context(active_id=context.get_model_var(model_name_2), res_model=model_name_2))
    context.set_model_form_var(model_name_1, form)


#######################################################
# When                                                #
# Performing actions, using Form, modifying variables #
#######################################################


## Form view


@when("I open the form view")
def when_i_open_the_form_view(context):
    context.assert_form_exists()


@when("I open a {model_name} form view")
def when_i_open_a_model_name_form_view(context, model_name):
    context.set_model_form_var(model_name, Form(self.env[model_name]))


@when("I open the {model_name} form view")
def when_i_open_the_model_name_form_view(context, model_name):
    context.set_model_form_var(model_name, context.get_model_form_var(model_name))


@when("I set the following fields:")
def when_i_set_the_following_fields(context):
    for row in context.table:
        field = row['field']
        value = row['alias_or_value']
        context.form[field] = context.alias_or_val(value)


@when("I set the field {field_name} to {alias_or_val}")
def when_i_set_the_field_field_name_to_alias_or_val(context, field_name, alias_or_val):
    context.form[field_name] = context.alias_or_val(alias_or_val)


# Switch to regex matcher for this step
use_step_matcher("re")


# Regex Breakdown:
# I create a new (?P<model_name>.+?)                  : Captures the model name (e.g., "sale order")
# for the (?P<field_name>[\w_]+) field in the form view : Captures the relational field (e.g., "partner_id")
# (?: ... )?                                          : An optional non-capturing group for the ending
# with fields:                                        : Matches the exact table suffix
# |                                                   : OR
# with (?P<inline_field>[\w_]+)\s*=\s*(?P<inline_value>.+) : Captures an inline field and value assignment
@when(r'I create a new (?P<model_name>.+?) for the field (?P<field_name>[\w_]+) in the form view(?: with fields:| with (?P<inline_field>[\w_]+)\s*=\s*(?P<inline_value>.+))?')
def when_i_create_a_new_model_name_for_the_field_in_form_view_with_fields(context, model_name, field_name, inline_field=None, inline_value=None):
    context.assert_form_exists()
    args = {}
    if context.table:
        args = {row['field']: context.alias_or_val(row['alias_or_value']) for row in context.table}

    elif inline_field and inline_value:
        # Strip potential quotes around the value (e.g., "hello" -> hello)
        args[inline_field] = context.alias_or_val(inline_value.strip('\'"'))

    form_model_name = context.form._record._name  # _record because the form might not be saved yet so no record
    # exceptions: bad names like order_line instead of sale_order_line_ids
    match (form_model_name, field_name):
        case ('sale.order', 'order_line' as f):
            with context.form.order_line.new() as order_line:  # simulates click on Add a line. Passes order_id automatically
                order_line['product_id'] = args['product_id']
        case (_m, f) if any(f.endswith(end) for end in ['_id', '_ids']):  # one2many, many2many, many2one
            # TODO: correct this like above
            context.form[field_name] = create_default(context, model_name, *args)
        case _:
            raise NotImplementedError(
                f"A case for model {model_name} and field {field_name} "
                "has not been implemented. Please implement it.",
            )


# Switch back to the default parser for subsequent steps in the file
use_step_matcher("parse")


@when("I save")
@when("I save the form")
@when("I save the form view")
def when_i_save_the_form_view(context):
    context.assert_form_exists()
    context.form.save()
    context.set_model_var(context.form.record._name, context.form.record)


@when("I save the {model_name} form")
@when("I save the {model_name} form view")
def when_i_save_the_model_name_form_view(context, model_name):
    form = context.get_model_form_var(model_name)
    form.save()

    context.set_model_var(model_name, form.record)


##


#############################
# Then                      #
# Asserts, expected results #
#############################


@then('there exists exactly one SOL with product "{name}" in the SO')
def then_there_exists_exactly_one_product_with_name_name_in_the_so(context, name):
    assert_exactly_one(context, 'sale.order.line',
        [('order_id', '=', context.sale_order.id), ('product_id.name', '=', name)])

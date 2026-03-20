import inspect
import re
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from behave import given as behave_given
from behave import then as behave_then
from behave import when as behave_when
from behave.runner import Context

# Regex to match 'model_name' exactly, or 'model_name_1', 'model_name_42', etc.
MODEL_PARAM_PATTERN = re.compile(r"^model_name(_\d+)?$")

# Define a TypeVar to preserve the signature of the decorated function
F = TypeVar("F", bound=Callable[..., Any])

# Literally a dictionary of words that the POs can use to refer to
# models that we can then use
MODEL_NAMES = {
    'product': 'product.product',
    'SO': 'sale.order',
    'SOL': 'sale.order.line',
    'work item': 'x_work_item',
    'work item line': 'x_work_item_line',
    'unit': 'uom.uom',
}


# fetch a word that is not a model _name in the dictionary (see above)
def translate_model_name(context, model_name):
    if (res := MODEL_NAMES.get(model_name, False)):
        return res
    try:
        context.self.env[model_name]
        return model_name
    except Exception:  # noqa: BLE001
        raise NotImplementedError(f"Either the model {model_name} or a translation has not been implemented.")


# translate_model_var_name('x_work_item_line', n=5)
# >>> x_work_item_line_5
# translate_model_var_name('product.product')
# >>> product_product
def translate_model_var_name(model_name, n=None):
    return model_name.replace('.', '_') + (f'_{n}' if n else '')


# add an alias for self for use in the function for commodity
# and to mimic the odoo test framework
def inject_self(context, func, args, kwargs):
    globs = func.__globals__
    globs['self'] = context.self
    return func(context, *args, **kwargs)


def _step_wrapper(decorator, step_text):
    """
    Replacer for behave's given, then, and when decorators
    that injects 'self' into the function's global namespace
    preserving their purpose.
    It also automatically translates any parameter named
    'model_name' or 'model_name_X' into its Odoo equivalent.
    """
    def wrapper(func):
        # Extract the signature of the step function once when it is decorated
        sig = inspect.signature(func)

        @wraps(func)
        def inner(context, *args, **kwargs):
            # Bind the incoming arguments to the parameter names in the function signature
            bound_args = sig.bind(context, *args, **kwargs)
            bound_args.apply_defaults()

            # Iterate over the bound arguments to find our target parameter names
            for param_name, param_value in bound_args.arguments.items():
                if MODEL_PARAM_PATTERN.match(param_name) and isinstance(param_value, str):
                    # Translate it and replace the value in the arguments dictionary
                    translated_model = translate_model_name(context, param_value)
                    bound_args.arguments[param_name] = translated_model

            # Extract the updated *args and **kwargs.
            # Since 'context' was passed into sig.bind() as the first argument,
            # it is at bound_args.args[0]. We slice [1:] to get the rest of the positional args.
            updated_args = bound_args.args[1:]
            updated_kwargs = bound_args.kwargs

            # Pass the translated arguments into your existing injector.
            return inject_self(context, func, updated_args, updated_kwargs)
        return decorator(step_text)(inner)
    return wrapper


def with_self(func: F) -> F:
    """
    Decorator that injects 'self' into the function's global namespace.
    'self' will be an alias for context.self with context being the
    first argument passed to the function (which is typically the
    'context' object in behave).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not args:
            return func(*args, **kwargs)
        return inject_self(args[0], func, args[1:], kwargs)
    return wrapper  # type: ignore


# --- RE-EXPORTED DECORATORS ---


def given(step_text: str):
    return _step_wrapper(behave_given, step_text)


def when(step_text: str):
    return _step_wrapper(behave_when, step_text)


def then(step_text: str):
    return _step_wrapper(behave_then, step_text)


# --- CONTEXT EXTENSIONS ---

# if a variable with that key exists, return it, otherwise return the key
def alias_or_val(self, aov):
    return getattr(self, aov, aov)


# Attach the method to the Context class
Context.alias_or_val = alias_or_val


# Example usage:
# context.get_model_var('sale.order', 1)
# -> Asserts existence, then returns context.sale_order_1
def get_model_var(self, model_name, n=None):
    return self.assert_model_var_exists(model_name, n)


Context.get_model_var = get_model_var


# Example usage:
# context.get_model_form_var('sale.order')
# -> Asserts existence, then returns context.sale_order_form
def get_model_form_var(self, model_name):
    return self.assert_model_form_var_exists(model_name)


Context.get_model_form_var = get_model_form_var


# Example usage:
# context.set_model_var('sale.order', sale.order(1,))
# -> sets context.sale_order = sale.order(1,)
# -> sets context.record = sale.order(1,)
def set_model_var(self, model_name, val, n=None):
    setattr(self, translate_model_var_name(model_name, n), val)
    setattr(self, 'record', val)
    return val


# Attach the method to the Context class
Context.set_model_var = set_model_var


# Example usage:
# context.set_model_form_var('sale.order', Form(sale.order(1,)))
# -> sets context.sale_order_form = Form(sale.order(1,))
# -> sets context.form = Form(sale.order(1,))
def set_model_form_var(self, model_name, val):
    setattr(self, translate_model_var_name(model_name) + '_form', val)
    setattr(self, 'form', val)
    return val


# Attach the method to the Context class
Context.set_model_form_var = set_model_form_var


# --- ASSERTS ---


def assert_exactly_one(context, model_name, domain):
    context.self.assertEqual(
        context.self.env[model_name].search_count(domain),
        1,
        f"Exactly one record should be present in {model_name}\nwith domain={domain}")


Context.assert_exactly_one = assert_exactly_one


def assert_record_exists(context, model_name):
    context.self.assertTrue(
        (res := context.record),
        "A record should exist (context.record)\nDo you have the right Given/When?")
    return res


Context.assert_record_exists = assert_record_exists


def assert_model_var_exists(context, model_name, n=None):
    # Dynamically build the variable name using your translator
    var_name = translate_model_var_name(model_name, n)
    res = getattr(context, var_name, None)

    context.self.assertTrue(
        res,
        f"A {model_name} record should exist (context.{var_name})\nDo you have the right Given/When?",
    )
    return res


Context.assert_model_var_exists = assert_model_var_exists


def assert_model_form_var_exists(context, model_name):
    var_name = translate_model_var_name(model_name) + '_form'
    res = getattr(context, var_name, None)

    context.self.assertTrue(
        res,
        f"A {model_name} form view should exist (context.{var_name})\nDo you have the right Given/When?",
    )
    return res


Context.assert_model_form_var_exists = assert_model_form_var_exists


def assert_form_exists(context):
    res = getattr(context, 'form', None)

    context.self.assertTrue(
        res,
        "A form view should exist (context.form)\nDo you have the right Given/When?",
    )
    return res


Context.assert_form_exists = assert_form_exists

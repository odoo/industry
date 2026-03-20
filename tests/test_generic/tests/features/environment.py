# Behave hooks

def before_all(context):
    # Setup variables used everywhere given by test_behave.py
    context.self = context.config.userdata['self']
    context._logger = context.config.userdata['_logger']
    context.industry_name = context.config.userdata['industry_name']
    context.industry_test_path = context.config.userdata['industry_test_path']


def before_feature(context, feature):
    pass


def before_scenario(context, scenario):
    # Create a database savepoint before each scenario starts
    context.odoo_savepoint = context.self.cr.savepoint()
    # Clear the cache to ensure scenario 2 doesn't see scenario 1's memory
    context.self.env.registry.clear_cache()


def before_step(context, step):
    pass


def after_step(context, step):
    pass


def after_scenario(context, scenario):
    # Roll back to the savepoint created in before_scenario
    context.odoo_savepoint.rollback()
    # Clear cache again
    context.self.env.registry.clear_cache()
    # Better here or in test_behave? Looks better in test_behave
#     # do not fail the whole test suite, but report all failed scenarios
#     with context.self.subTest(industry=context.industry_name, feature=scenario.feature.name, scenario=scenario.name):
#         for step in scenario.steps:
#             if step.status.name == 'undefined':
#                 context._logger.warning(
#                     "Step %s is not defined.",
#                     step.name,
#                 )
#             else:
#                 context.self.assertNotIn(step.status.name, ['failed', 'error'], f"""
# Behave test failed in module '{context.industry_name}' for feature '{scenario.feature.name}' in scenario '{scenario.name}'.
# Step: '{step.keyword} {step.name}'
# {step.error_message}""")


def after_feature(context, feature):
    pass


def after_all(context):
    pass

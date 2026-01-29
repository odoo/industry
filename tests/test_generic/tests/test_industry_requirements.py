# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
import pathlib
import re

from lxml import etree

from odoo.tests import get_db_name, tagged
from odoo.tools import cloc

from .industry_case import IndustryCase, get_industry_path

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestEnv(IndustryCase):

    def test_payment_demo(self):
        db_name = get_db_name()
        if db_name.endswith('imported_no_demo'):
            return
        no_online_payment_industries = [
            'bike_leasing',
            'real_estate',
        ]
        if any(m in self.installed_industries for m in no_online_payment_industries):
            # we don't pay the cart in this industry, we get a quote or fill a form
            return
        all_dependencies = self.env["ir.module.module.dependency"].all_dependencies(self.installed_industries)
        if any('website_payment' in deps for deps in all_dependencies.values()):
            self.assertTrue(
                self.env['ir.module.module']._get('payment_demo').state == 'installed',
                "Payment Demo module should be installed in demo when Website Payment is installed. "
                "Call 'button_immediate_install' on 'base.module_payment_demo' in demo.",
            )

    def test_welcome_article_and_notification_exist(self):
        for module in self.installed_industries:
            if module in ['construction_developer']:
                continue
            ref = self.env.ref(f"{module}.welcome_article", raise_if_not_found=False)
            self.assertTrue(
                ref, f"You forgot to define a record with id='welcome_article' in module '{module}'.",
            )
            ref = self.env.ref(f"{module}.welcome_article_body", raise_if_not_found=False)
            self.assertTrue(
                ref, f"You forgot to define a template with id='welcome_article_body' in module '{module}'.",
            )
            if not (ref := self.env.ref(module + '.notification_knowledge', raise_if_not_found=False)):
                _logger.warning("You forgot to define a `mail.message` with `id=notification_knowledge`.")
            notif = ref and self.env['mail.message'].browse(ref.id)
            if notif and '/odoo/knowledge/' not in notif.body:
                _logger.warning("The mail.message should contain a link to the knowledge article.")
            if notif and 'Get started with' not in notif.subject:
                _logger.warning("The mail.message subject is wrong: %s.", notif.subject)

            knowledge = self.env.ref(f"{module}.welcome_article", raise_if_not_found=False)
            if not knowledge:
                _logger.warning("Missing knowledge article for the industry module.")
            if knowledge.favorite_count == 0:
                _logger.warning("The knowledge article should be in the favorite category")
            if notif and knowledge and '/odoo/knowledge/%s' % knowledge.id not in notif.body:
                _logger.warning("The notification link should target the module-related knowledge article.")

    def test_cloc_exclude_view(self):
        c = cloc.Cloc()
        c.count_database(self.env.cr.dbname)
        c.report(True)  # show details of cloc in the logs
        for module in self.installed_modules:
            for cloc_entry in c.modules.get(module, {}):
                message = "The record '%s' is counted in the maintenance lines. " % cloc_entry
                message += "Please add the file in 'cloc_exclude' list of the manifest."
                self.assertIn(cloc_entry.split('/')[0], ['ir.actions.server', 'ir.model.fields'], message)

    def test_sale_ok_and_is_published_in_db(self):
        models = ["product.template", "product.product"]
        for model in models:
            if model in self.env and "is_published" in self.env[model]._fields:
                records = self.env[model].search(
                    [("is_published", "=", True), ("sale_ok", "=", False)],
                )

                self.assertFalse(
                    records,
                    "Found records with 'is_published=True' and 'sale_ok=False' in the database. Records: %s"
                    % ", ".join(
                        ["%s (ID: %s)" % (record.display_name, record.id) for record in records],
                    ),
                )

    def test_knowledge_article_links_use_latest(self):
        pattern = r'https?://www\.odoo\.com/documentation/(?!latest/)(.*)/'
        for module in self.installed_modules:
            knowledges = self.env['ir.model.data'].search(
                [('model', '=', 'knowledge.article'), ('module', '=', module)],
            )
            if not knowledges:
                continue
            for knowledge in knowledges:
                knowledge_article = self.env.ref(knowledge.complete_name)
                content = knowledge_article.body or ''
                matches = re.findall(pattern, content)
                self.assertFalse(
                    matches,
                    "Found links to Odoo documentation using version-specific URLs in module '%s' knowledge article: %s. Please use '/latest/' instead."
                    % (module, matches),
                )

    @staticmethod
    def _are_pos_config_and_onboarding_used(path, folder_data, folder_name):
        pos_config_defined = False
        pos_config_count = 0
        load_onboarding_called = False
        load_count = 0
        for file_name in folder_data:
            file_path = os.path.join(path, folder_name, file_name)
            encoded_content = pathlib.Path(file_path).read_bytes()
            try:
                tree = etree.fromstring(encoded_content)
            except etree.XMLSyntaxError as e:
                _logger.error("XML syntax error in file %s: %s", file_name, e)
                return False, 0, False, 0
            for record in tree.xpath("//function[@model='pos.config']"):
                function_name = record.get('name')
                if 'load_onboarding_' in function_name:
                    load_onboarding_called = True
                    load_count += 1
            for record in tree.xpath("//record"):
                model_name = record.get('model')
                if model_name == 'pos.config':
                    pos_config_defined = True
                    pos_config_count += 1
        return pos_config_defined, pos_config_count, load_onboarding_called, load_count

    def test_pos_requirements(self):
        all_dependencies = self.env["ir.module.module.dependency"].all_dependencies(self.installed_industries)
        if not any('point_of_sale' in deps for deps in all_dependencies.values()):
            return
        for module in self.installed_industries:
            path = get_industry_path() + module
            data, demo = [], []
            for root, dirs, files in os.walk(path):
                for file_name in files:
                    if file_name.endswith('.xml'):
                        if root.split('/')[-1] == 'data':
                            data.append(file_name)
                        elif root.split('/')[-1] == 'demo':
                            demo.append(file_name)
            data_pos_config_defined, data_pos_count, data_load_onboarding_called, data_load_count = TestEnv._are_pos_config_and_onboarding_used(path, data, 'data')
            demo_pos_config_defined, demo_pos_count, demo_load_onboarding_called, demo_load_count = TestEnv._are_pos_config_and_onboarding_used(path, demo, 'demo')
            if demo_pos_config_defined and not demo_load_onboarding_called and not data_load_onboarding_called:
                _logger.warning(
                    "In module '%s', a pos.config is defined in the demo, but no load_onboarding_ scenario function is called in the data or in the demo. You should load a scenario in the data to set up the POS properly, and if needed overwrite some fields.",
                    module,
                )
            elif demo_load_onboarding_called and not data_load_onboarding_called:
                _logger.warning(
                    "In module '%s', a load_onboarding_ scenario function is called in the demo, but not in the data. You should call it in the data to set up the POS properly.",
                    module,
                )
            elif data_pos_config_defined and not data_load_onboarding_called:
                _logger.warning(
                    "In module '%s', a pos.config is defined in the data, but no load_onboarding_ scenario function is called in the data. You should load a scenario in the data to set up the POS properly, and if needed overwrite some fields.",
                    module,
                )
            elif not data_pos_config_defined and not data_load_onboarding_called:
                _logger.warning(
                    "The module '%s' depends on point_of_sale, but no load_onboarding_ scenario function is called in the data. You should load a scenario in the data to set up the POS properly.",
                    module,
                )
            elif data_load_count < data_pos_count:
                _logger.warning(
                    "In module '%s', the number of pos.config defined in data (%d) does not match the number of load_onboarding_ scenario functions called in data (%d). Each pos.config should be set up by a load_onboarding_ function.",
                    module,
                    data_pos_count,
                    data_load_count,
                )
            elif demo_pos_count > demo_load_count + data_load_count:
                _logger.warning(
                    "In module '%s', the number of pos.config defined in demo (%d) is greater than the total number of load_onboarding_ scenario functions called in data and demo (%d). Each pos.config should be set up by a load_onboarding_ function.",
                    module,
                    demo_pos_count,
                    demo_load_count + data_load_count,
                )

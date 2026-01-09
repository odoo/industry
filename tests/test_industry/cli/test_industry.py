# -*- coding: UTF-8 -*-
import logging
import optparse
import pathlib
import sys
import time

from odoo import api, sql_db
from odoo.cli.command import Command
from odoo.modules.registry import Registry
from odoo.service import server
from odoo.tests import loader
from odoo.tests.result import OdooTestResult
from odoo.tools import config

from ..modules import db

sys.path.append(pathlib.Path(__file__).parent.parent.parent.parent.as_posix())
import utils

_logger = logging.getLogger(__name__)

ROOT_PATH = pathlib.Path(__file__).parent.parent.parent.parent


class Test_Industry(Command):
    def run(self, args):
        parser = config.parser
        group = optparse.OptionGroup(parser, "Industry Configuration")
        group.add_option('--all', dest='all', action='store_true', help='Install all industry modules found in the industry folder')
        group.add_option('--industries', dest='industries', help='List of industry modules to install')
        group.add_option('--singledb', dest='singledb', help='Duplicate the database and loads each industry module in its own database')
        group.add_option('--drop-if-exists', dest='drop_if_exists', action='store_true', help='Dropdb if it already exists')
        group.add_option('--industry-demo', dest='industry_demo', action='store_true', help='Load industry modules with demo data')

        parser.add_option_group(group)
        config.parse_config(['--no-http'] + args, setup_logging=True)
        if config.get('all'):
            industry_modules = sorted([p.name for p in (ROOT_PATH).iterdir() if p.is_dir() and (p / '__manifest__.py').exists()])
        else:
            industry_modules = (config['industries'] or '').split(',')
        if not industry_modules:
            raise ValueError("You must provide industry modules to install using --industries=industry_module or use --all")
        config['init'] = []
        test_enable = config['test_enable']
        config['test_enable'] = False
        test_tags = config['test_tags']
        if test_tags == "+standard" and test_enable:
            test_tags = None
        config['test_tags'] = ''
        config["registry_lru_size"] = 1  # don't keep all registry in memory, and ensure a single registry when running tests

        init_db = config["db_name"][0]
        registry = None
        #registry = Registry(init_db)
        #with registry.cursor() as cr:
        #    env = api.Environment(cr, api.SUPERUSER_ID, {})
        #    env['ir.qweb']._pregenerate_assets_bundles()

        for industry_module in industry_modules:
            try:
                install = True
                zip_content = utils.IndustryUtils().get_zip(industry_module)
                if config.get('singledb'):
                    target_db = init_db
                    registry = Registry(target_db)
                else:
                    target_db = f"{init_db}-{industry_module}"
                    if db.exist(target_db):
                        if config.get('drop_if_exists'):
                            db.drop(target_db)
                        elif test_enable:
                            _logger.info('Database %s already exists, skipping industry module install%s', target_db, industry_module)
                            install = False
                        else:
                            raise ValueError(f"Database {target_db} already exists, use --drop-if-exists to drop it before installing the industry module {industry_module}")
                    if install:
                        db.duplicate(init_db, target_db)
                    registry = Registry(target_db)
                if install:
                    with registry.cursor() as cr:
                        env = api.Environment(cr, api.SUPERUSER_ID, {'active_test': False})
                        with_demo = config.get('industry_demo') or config['with_demo']
                        _logger.info('Loading module %s into database %s %s', industry_module, target_db, with_demo and 'with demo data' or '')
                        existing_module = env['ir.module.module'].search([])
                        env['ir.module.module']._import_zipfile(zip_content, force=False, with_demo=with_demo)
                        env['ir.module.module'].search([('id', 'not in', existing_module.ids)]).demo = with_demo
                        env.cr.commit()
                if test_enable:
                    try:
                        config['test_enable'] = True
                        registry._assertion_report = OdooTestResult()
                        test_modules = ['test_generic']
                        test_industry_name = f'test_{industry_module}'
                        if (ROOT_PATH / "tests" / test_industry_name).exists():
                            test_modules.append(test_industry_name)
                        with registry.cursor() as cr:
                            env = api.Environment(cr, api.SUPERUSER_ID, {})
                            modules = env['ir.module.module'].search([('name', 'in', test_modules)])
                            modules.button_immediate_install()
                        if test_tags:
                            config['test_tags'] = test_tags
                        else:
                            config['test_tags'] = ','.join([f"/{module}" for module in test_modules])

                        config['db_name'] = target_db
                        _logger.info('Running tests for industry module %s in database %s', industry_module, target_db)
                        server.start(preload=[target_db], stop=True)
                    finally:
                        config['test_enable'] = False
                        config['test_tags'] = ''
                        config['init'] = []
            except Exception:
                _logger.exception('Error while installing industry module %s', industry_module)

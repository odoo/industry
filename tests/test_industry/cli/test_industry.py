# -*- coding: UTF-8 -*-
import logging
import optparse
import pathlib
import sys
import time

from odoo import api, sql_db
from odoo.cli.command import Command
from odoo.modules.registry import Registry
from odoo.tests import loader  # noqa: PLC0415
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
        config['test_tags'] = ''

        init_db = config["db_name"][0]
        registry = None

        for industry_module in industry_modules:
            try:
                zip_content = utils.IndustryUtils().get_zip(industry_module)
                if config.get('singledb'):
                    target_db = init_db
                    if not registry:
                        registry = Registry(init_db)
                else:
                    target_db = f"{init_db}-{industry_module}"
                    if config.get('drop_if_exists') and db.exist(target_db):
                        db.drop(target_db)
                    db.duplicate(init_db, target_db)
                    registry = Registry(target_db)
                with registry.cursor() as cr:
                    env = api.Environment(cr, api.SUPERUSER_ID, {'active_test': False})
                    with_demo = config.get('industry_demo') or config['with_demo']
                    _logger.info('Loading module %s into database %s %s', industry_module, target_db, with_demo and 'with demo data' or '')
                    existing_module = env['ir.module.module'].search([])
                    env['ir.module.module']._import_zipfile(zip_content, force=False, with_demo=with_demo)
                    env['ir.module.module'].search([('id', 'not in', existing_module.ids)]).demo = with_demo
                    env.cr.commit()
                if test_enable:
                    config['test_enable'] = True
                    config['test_tags'] = test_tags
                    config['db_name'] = target_db
                    _logger.info('Running tests for industry module %s in database %s', industry_module, target_db)
                    modules = ['test_generic']
                    test_industry_name = f'test_{industry_module}'
                    if (ROOT_PATH / "tests" / test_industry_name).exists():
                        modules.append(test_industry_name)
                        # todo install the test module?
                    t0 = time.time()
                    t0_sql = sql_db.sql_counter
                    post_install_suite = loader.make_suite(modules, 'post_install')
                    result = loader.run_suite(post_install_suite)
                    _logger.info("%d post-tests in %.2fs, %s queries",
                                result.testsRun,
                                time.time() - t0,
                                sql_db.sql_counter - t0_sql)
                    config['test_enable'] = False
                    config['test_tags'] = ''
            except Exception:
                _logger.exception('Error while installing industry module %s', industry_module)

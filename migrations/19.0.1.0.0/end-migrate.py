# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Rewrite salary rules to use `version` and ensure rules exist on all structures."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.hr_back_pay.hooks import ensure_back_pay_salary_rules
    ensure_back_pay_salary_rules(env)

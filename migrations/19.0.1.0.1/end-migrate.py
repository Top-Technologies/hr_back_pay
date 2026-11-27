# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Rewrite BACK_PAY_PENSION_7 Python to drop getattr() (not available in safe_eval)."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.hr_back_pay.hooks import ensure_back_pay_salary_rules
    ensure_back_pay_salary_rules(env)

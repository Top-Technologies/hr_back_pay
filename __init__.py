# -*- coding: utf-8 -*-
from . import models


def post_init_hook(env):
    """Ensure back-pay salary rules exist on every payroll structure."""
    from .hooks import ensure_back_pay_salary_rules
    ensure_back_pay_salary_rules(env)

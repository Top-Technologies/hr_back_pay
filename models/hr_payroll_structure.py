# -*- coding: utf-8 -*-
from odoo import api, models

from ..hooks import ensure_back_pay_salary_rules


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    @api.model_create_multi
    def create(self, vals_list):
        structures = super().create(vals_list)
        ensure_back_pay_salary_rules(self.env)
        return structures

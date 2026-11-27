# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    """Expose version back-pay fields on the employee form (Odoo 19 _inherits pattern)."""
    _inherit = 'hr.employee'

    allowance_retroactive = fields.Float(
        related='version_id.allowance_retroactive',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_months = fields.Integer(
        related='version_id.back_pay_months',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_previous_net = fields.Float(
        related='version_id.back_pay_previous_net',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_previous_tax = fields.Float(
        related='version_id.back_pay_previous_tax',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_previous_pension = fields.Float(
        related='version_id.back_pay_previous_pension',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_new_net = fields.Float(
        related='version_id.back_pay_new_net',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_monthly_diff = fields.Float(
        related='version_id.back_pay_monthly_diff',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_total = fields.Float(
        related='version_id.back_pay_total',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_tax_monthly = fields.Float(
        related='version_id.back_pay_tax_monthly',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_tax_total = fields.Float(
        related='version_id.back_pay_tax_total',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_pension_monthly = fields.Float(
        related='version_id.back_pay_pension_monthly',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_pension_total = fields.Float(
        related='version_id.back_pay_pension_total',
        readonly=True,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    is_back_pay_approved = fields.Boolean(
        related='version_id.is_back_pay_approved',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    back_pay_justification = fields.Char(
        related='version_id.back_pay_justification',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )
    has_pension = fields.Boolean(
        related='version_id.has_pension',
        readonly=False,
        inherited=True,
        groups='hr_payroll.group_hr_payroll_user',
    )

    def action_fetch_previous_payslip(self):
        return self.version_id.action_fetch_previous_payslip()

    def action_approve_back_pay(self):
        return self.version_id.action_approve_back_pay()

    def action_reset_back_pay(self):
        return self.version_id.action_reset_back_pay()

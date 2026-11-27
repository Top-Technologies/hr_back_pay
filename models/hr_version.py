# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrVersion(models.Model):
    _inherit = 'hr.version'

    allowance_retroactive = fields.Float(
        string='Back Payment / Retroactive Pay (የተከማቸ የደመወዝ ጭማሪ)',
        digits=(16, 2),
        default=0.0,
        tracking=True,
        help='Salary difference resulting from approved retroactive salary adjustments.',
    )
    back_pay_months = fields.Integer(
        string='Retroactive Months (የወራት ብዛት)',
        default=0,
        tracking=True,
        help='Number of retroactive months to calculate and pay the salary difference for.',
    )
    back_pay_previous_net = fields.Float(
        string='Previous Monthly Net Salary (የቀድሞ የተጣራ ደመወዝ)',
        digits=(16, 2),
        default=0.0,
        tracking=True,
        help='The actual net monthly take-home salary the employee received prior to the approved raise.',
    )
    back_pay_previous_tax = fields.Float(
        string='Previous Monthly Income Tax (የቀድሞ የገቢ ግብር)',
        digits=(16, 2),
        default=0.0,
        tracking=True,
        help='Monthly income tax from previous payslip before retroactive adjustment.',
    )
    back_pay_previous_pension = fields.Float(
        string='Previous Monthly Pension 7% (የቀድሞ ጡረታ 7%)',
        digits=(16, 2),
        default=0.0,
        tracking=True,
        help='Monthly 7% employee pension from previous payslip before retroactive adjustment.',
    )
    back_pay_new_net = fields.Float(
        string='Corrected Monthly Net Salary (አዲሱ የተጣራ ደመወዝ)',
        compute='_compute_back_pay',
        store=True,
        readonly=False,
        digits=(16, 2),
        tracking=True,
        help='The corrected monthly net salary with the approved raise (Regular Net Wage).',
    )
    back_pay_monthly_diff = fields.Float(
        string='Monthly Back Pay Difference (ወርሃዊ ልዩነት)',
        compute='_compute_back_pay',
        store=True,
        digits=(16, 2),
        help='Monthly Back Pay = Corrected Net Salary - Previous Net Salary.',
    )
    back_pay_total = fields.Float(
        string='Total Back Pay Amount (ጠቅላላ የተከማቸ ክፍያ)',
        compute='_compute_back_pay',
        store=True,
        digits=(16, 2),
        help='Total Back Pay = Monthly Difference × Number of Months.',
    )
    back_pay_tax_monthly = fields.Float(
        string='Monthly Back Pay Income Tax (ወርሃዊ የተከማቸ የገቢ ግብር)',
        compute='_compute_back_pay',
        store=True,
        digits=(16, 2),
        help='Monthly income tax difference between new and previous wage.',
    )
    back_pay_tax_total = fields.Float(
        string='Total Back Pay Income Tax (ጠቅላላ የተከማቸ የገቢ ግብር)',
        compute='_compute_back_pay',
        store=True,
        digits=(16, 2),
        help='Total income tax for the retroactive period (for government reporting, not deducted from net).',
    )
    back_pay_pension_monthly = fields.Float(
        string='Monthly Back Pay Pension 7% (ወርሃዊ የተከማቸ ጡረታ 7%)',
        compute='_compute_back_pay',
        store=True,
        digits=(16, 2),
        help='Monthly 7% employee pension difference between new and previous wage.',
    )
    back_pay_pension_total = fields.Float(
        string='Total Back Pay Pension 7% (ጠቅላላ የተከማቸ ጡረታ 7%)',
        compute='_compute_back_pay',
        store=True,
        digits=(16, 2),
        help='Total 7% employee pension for the retroactive period (for government reporting, not deducted from net).',
    )
    is_back_pay_approved = fields.Boolean(
        string='Finance Manager Approval (የፋይናንስ ማረጋገጫ)',
        default=False,
        tracking=True,
        help='Finance Manager approval is required before retroactive back pay is included on payslips.',
    )
    back_pay_justification = fields.Char(
        string='Back Pay Reason / Period Note',
        tracking=True,
        help='e.g. Retroactive promotion approved from Tir to Megabit.',
    )
    # Used by BACK_PAY_PENSION_7 rule when Farm Management is not installed
    has_pension = fields.Boolean(
        string='Pension Scheme (የጡረታ ተጠቃሚ)',
        default=True,
        tracking=True,
        help='When disabled, back-pay pension reporting amount is skipped.',
    )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _back_pay_float(self, name, default=0.0):
        """Read optional farm/payroll fields safely when this module runs alone."""
        self.ensure_one()
        return getattr(self, name, default) or default

    def _ethiopian_income_tax(self, taxable):
        taxable = taxable or 0.0
        if taxable <= 2000:
            tax = 0.0
        elif taxable <= 4000:
            tax = 0.15 * taxable - 300.0
        elif taxable <= 7000:
            tax = 0.20 * taxable - 500.0
        elif taxable <= 10000:
            tax = 0.25 * taxable - 850.0
        elif taxable <= 14000:
            tax = 0.30 * taxable - 1350.0
        else:
            tax = 0.35 * taxable - 2050.0
        return round(max(0.0, tax), 2)

    def _compute_regular_net_and_tax(self):
        """Return (regular_net, new_tax, new_pension) for the corrected monthly salary."""
        self.ensure_one()
        c = self
        wage = c.wage or 0.0
        ot_amt = c._back_pay_float('total_ot_amount') or c._back_pay_float('allowance_overtime')
        transport = c._back_pay_float('allowance_transport')
        hardship = c._back_pay_float('allowance_hardship')
        cash_indemnity = c._back_pay_float('allowance_cash_indemnity')
        other_allowances = c._back_pay_float('total_other_allowances')
        acting = c._back_pay_float('allowance_acting_position')
        bulk = c._back_pay_float('allowance_bulk_loading')
        allowance_other = c._back_pay_float('allowance_other')
        taxable_transport = c._back_pay_float('taxable_transport_allowance')
        total_deductions = c._back_pay_float('total_monthly_deductions')
        has_pension = bool(getattr(c, 'has_pension', True))

        regular_gross = (
            wage + transport + hardship + ot_amt + cash_indemnity + other_allowances
        )
        regular_net = max(0.0, regular_gross - total_deductions)

        new_pension = round(wage * 0.07, 2) if has_pension else 0.0
        taxable = (
            wage + taxable_transport + hardship + ot_amt
            + acting + bulk + allowance_other
        )
        new_tax = c._ethiopian_income_tax(taxable)
        return regular_net, new_tax, new_pension

    # -------------------------------------------------------------------------
    # Back Pay / Retroactive Adjustment Computation & Logic
    # -------------------------------------------------------------------------
    def action_fetch_previous_payslip(self):
        """Fetch previous net, income tax, and pension 7% from last confirmed payslip."""
        for version in self:
            version._fetch_previous_payslip_data()

    def _fetch_previous_payslip_data(self):
        for version in self:
            if not version.employee_id:
                continue
            # Odoo 19 payslip states: draft / validated / paid / cancel
            payslip = self.env['hr.payslip'].search([
                ('employee_id', '=', version.employee_id.id),
                ('state', 'in', ('validated', 'paid')),
            ], order='date_to desc, id desc', limit=1)
            if not payslip:
                payslip = self.env['hr.payslip'].search([
                    ('employee_id', '=', version.employee_id.id),
                    ('state', '!=', 'cancel'),
                ], order='date_to desc, id desc', limit=1)
            if not payslip:
                continue

            net_line = payslip.line_ids.filtered(lambda l: l.code == 'NET')
            net_val = net_line[0].total if net_line else payslip.net_wage
            version.back_pay_previous_net = net_val or 0.0

            tax_line = payslip.line_ids.filtered(lambda l: l.code == 'DED_INCOME_TAX')
            version.back_pay_previous_tax = abs(tax_line[0].total) if tax_line else 0.0

            pension_line = payslip.line_ids.filtered(lambda l: l.code == 'DED_PENSION_7')
            version.back_pay_previous_pension = abs(pension_line[0].total) if pension_line else 0.0

    @api.depends(
        'back_pay_months',
        'back_pay_previous_net',
        'back_pay_previous_tax',
        'back_pay_previous_pension',
        'wage',
        'has_pension',
        'allowance_retroactive',
    )
    def _compute_back_pay(self):
        for c in self:
            regular_net, new_tax, new_pension = c._compute_regular_net_and_tax()
            c.back_pay_new_net = regular_net

            prev_tax = c.back_pay_previous_tax or 0.0
            prev_pension = c.back_pay_previous_pension or 0.0
            monthly_tax_diff = (
                max(0.0, round(new_tax - prev_tax, 2))
                if (new_tax > prev_tax and prev_tax > 0) else 0.0
            )
            monthly_pension_diff = (
                max(0.0, round(new_pension - prev_pension, 2))
                if (new_pension > prev_pension and prev_pension > 0) else 0.0
            )

            if c.back_pay_months > 0 and c.back_pay_previous_net > 0:
                monthly_diff = max(0.0, round(regular_net - c.back_pay_previous_net, 2))
                total_back_pay = round(monthly_diff * c.back_pay_months, 2)
                c.back_pay_monthly_diff = monthly_diff
                c.back_pay_total = total_back_pay
                c.allowance_retroactive = total_back_pay
                c.back_pay_tax_monthly = monthly_tax_diff
                c.back_pay_tax_total = round(monthly_tax_diff * c.back_pay_months, 2)
                c.back_pay_pension_monthly = monthly_pension_diff
                c.back_pay_pension_total = round(monthly_pension_diff * c.back_pay_months, 2)
            elif c.back_pay_months > 0 and c.allowance_retroactive > 0:
                c.back_pay_total = c.allowance_retroactive
                c.back_pay_monthly_diff = round(c.allowance_retroactive / c.back_pay_months, 2)
                c.back_pay_tax_monthly = monthly_tax_diff
                c.back_pay_tax_total = round(monthly_tax_diff * c.back_pay_months, 2)
                c.back_pay_pension_monthly = monthly_pension_diff
                c.back_pay_pension_total = round(monthly_pension_diff * c.back_pay_months, 2)
            else:
                c.back_pay_monthly_diff = 0.0
                c.back_pay_total = c.allowance_retroactive or 0.0
                c.back_pay_tax_monthly = 0.0
                c.back_pay_tax_total = 0.0
                c.back_pay_pension_monthly = 0.0
                c.back_pay_pension_total = 0.0

    @api.onchange('back_pay_months', 'back_pay_previous_net', 'wage', 'has_pension')
    def _onchange_back_pay_calculator(self):
        if self.back_pay_months > 0 and not self.back_pay_previous_net:
            self._fetch_previous_payslip_data()

        regular_net, new_tax, new_pension = self._compute_regular_net_and_tax()
        self.back_pay_new_net = regular_net

        prev_tax = self.back_pay_previous_tax or 0.0
        prev_pension = self.back_pay_previous_pension or 0.0
        monthly_tax_diff = (
            max(0.0, round(new_tax - prev_tax, 2))
            if (new_tax > prev_tax and prev_tax > 0) else 0.0
        )
        monthly_pension_diff = (
            max(0.0, round(new_pension - prev_pension, 2))
            if (new_pension > prev_pension and prev_pension > 0) else 0.0
        )

        if self.back_pay_months > 0 and self.back_pay_previous_net > 0:
            monthly_diff = max(0.0, round(regular_net - self.back_pay_previous_net, 2))
            total_back_pay = round(monthly_diff * self.back_pay_months, 2)
            self.back_pay_monthly_diff = monthly_diff
            self.back_pay_total = total_back_pay
            self.allowance_retroactive = total_back_pay
            self.back_pay_tax_monthly = monthly_tax_diff
            self.back_pay_tax_total = round(monthly_tax_diff * self.back_pay_months, 2)
            self.back_pay_pension_monthly = monthly_pension_diff
            self.back_pay_pension_total = round(monthly_pension_diff * self.back_pay_months, 2)

    def action_approve_back_pay(self):
        for version in self:
            version.is_back_pay_approved = True

    def action_reset_back_pay(self):
        for version in self:
            version.write({
                'back_pay_months': 0,
                'back_pay_previous_net': 0.0,
                'back_pay_previous_tax': 0.0,
                'back_pay_previous_pension': 0.0,
                'back_pay_tax_monthly': 0.0,
                'back_pay_tax_total': 0.0,
                'back_pay_pension_monthly': 0.0,
                'back_pay_pension_total': 0.0,
                'back_pay_monthly_diff': 0.0,
                'back_pay_total': 0.0,
                'allowance_retroactive': 0.0,
                'is_back_pay_approved': False,
                'back_pay_justification': False,
            })

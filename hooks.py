# -*- coding: utf-8 -*-

BACK_PAY_RULE_CODES = ('ALW_RETROACTIVE', 'BACK_PAY_TAX', 'BACK_PAY_PENSION_7')


def _rule_defs(env):
    """Salary-rule definitions using Odoo 19 localdict key `version` (not `contract`)."""
    Category = env['hr.salary.rule.category'].sudo()

    alw_category = env.ref('hr_payroll.ALW', raise_if_not_found=False)
    summary_category = env.ref('hr_back_pay.category_payslip_summary', raise_if_not_found=False)
    if not summary_category:
        summary_category = Category.search([('code', '=', 'SUMMARY')], limit=1)
    if not summary_category:
        summary_category = Category.create({
            'name': 'Payslip Summary & Informational Reporting (የደመወዝ ማጠቃለያ)',
            'code': 'SUMMARY',
            # Global like hr_payroll.ALW — required when rules are added to all structures
            'country_id': False,
        })
    elif summary_category.country_id:
        # Clear country if a previous install left company-country default (blocks multi-country structs)
        summary_category.country_id = False

    return [
        {
            'code': 'ALW_RETROACTIVE',
            'name': 'Back Payment / Retroactive Pay (የተከማቸ የደመወዝ ጭማሪ - ከግብር ነፃ)',
            'sequence': 30,
            'category_id': alw_category.id if alw_category else False,
            'condition_python': (
                "result = bool(version.allowance_retroactive and "
                "version.allowance_retroactive > 0 and "
                "(version.is_back_pay_approved or not version.back_pay_months))"
            ),
            'amount_python_compute': 'result = version.allowance_retroactive',
        },
        {
            'code': 'BACK_PAY_TAX',
            'name': 'Back Pay Income Tax (የተከማቸ ጭማሪ የገቢ ግብር - ለሪፖርት)',
            'sequence': 180,
            'category_id': summary_category.id,
            'condition_python': (
                "result = bool(version.back_pay_tax_total and "
                "version.back_pay_tax_total > 0 and "
                "(version.is_back_pay_approved or not version.back_pay_months))"
            ),
            'amount_python_compute': 'result = version.back_pay_tax_total',
        },
        {
            'code': 'BACK_PAY_PENSION_7',
            'name': 'Back Pay Employee Pension 7% (የተከማቸ ጭማሪ ጡረታ 7% - ለሪፖርት)',
            'sequence': 181,
            'category_id': summary_category.id,
            # No getattr(): salary-rule safe_eval does not expose it
            'condition_python': (
                "result = bool(version.has_pension and "
                "version.back_pay_pension_total and "
                "version.back_pay_pension_total > 0 and "
                "(version.is_back_pay_approved or not version.back_pay_months))"
            ),
            'amount_python_compute': (
                "result = version.back_pay_pension_total if version.has_pension else 0.0"
            ),
        },
    ]


def rewrite_legacy_contract_salary_rules(env):
    """Rewrite pre-19 salary-rule Python that still references `contract.`."""
    Rule = env['hr.salary.rule'].sudo()
    rules = Rule.search([('code', 'in', list(BACK_PAY_RULE_CODES))])
    for rule in rules:
        vals = {}
        for field_name in ('condition_python', 'amount_python_compute'):
            code = rule[field_name] or ''
            if 'contract.' in code:
                vals[field_name] = code.replace('contract.', 'version.')
        if vals:
            rule.write(vals)


def ensure_back_pay_salary_rules(env):
    """Create ALW_RETROACTIVE / BACK_PAY_TAX / BACK_PAY_PENSION_7 on each structure if missing."""
    rewrite_legacy_contract_salary_rules(env)

    Rule = env['hr.salary.rule'].sudo()
    rule_defs = _rule_defs(env)
    structures = env['hr.payroll.structure'].sudo().search([])
    for structure in structures:
        for rule_def in rule_defs:
            if not rule_def.get('category_id'):
                continue
            existing = Rule.search([
                ('code', '=', rule_def['code']),
                ('struct_id', '=', structure.id),
            ], limit=1)
            if existing:
                # Keep definitions in sync with Odoo 19 `version` localdict
                existing.write({
                    'condition_select': 'python',
                    'condition_python': rule_def['condition_python'],
                    'amount_select': 'code',
                    'amount_python_compute': rule_def['amount_python_compute'],
                    'category_id': rule_def['category_id'],
                    'sequence': rule_def['sequence'],
                })
                continue
            Rule.create({
                'name': rule_def['name'],
                'code': rule_def['code'],
                'sequence': rule_def['sequence'],
                'category_id': rule_def['category_id'],
                'struct_id': structure.id,
                'condition_select': 'python',
                'condition_python': rule_def['condition_python'],
                'amount_select': 'code',
                'amount_python_compute': rule_def['amount_python_compute'],
            })

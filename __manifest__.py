# -*- coding: utf-8 -*-
{
    'name': 'HR Back Pay / Retroactive Pay',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Version-based back pay / retroactive salary adjustments with payslip integration',
    'description': """
HR Back Pay / Retroactive Pay
=============================
Standalone payroll add-on extracted from Farm Management.

Features:
- Retroactive months calculator on employee versions (contracts)
- Fetch previous payslip net / tax / pension
- Finance Manager approval gate before payslip inclusion
- Salary rules:
  * ALW_RETROACTIVE — Back Payment (untaxed net payable)
  * BACK_PAY_TAX — Back Pay Income Tax (reporting only)
  * BACK_PAY_PENSION_7 — Back Pay Employee Pension 7% (reporting only)

Compatible with Odoo 19 Enterprise (hr_payroll).
Uses hr.version (contracts merged into versioned employees in 19.0).
    """,
    'author': 'Top Technologies',
    'website': 'https://www.odoo.com',
    'depends': ['hr', 'hr_payroll', 'mail'],
    'data': [
        'data/hr_payroll_data.xml',
        'views/hr_back_pay_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}

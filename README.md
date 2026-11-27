# HR Back Pay / Retroactive Pay

Standalone Odoo **19 Enterprise** module extracted from **Farm Management**. Adds back-pay / retroactive salary adjustment on employee versions and payslips.

> Odoo 19 replaces `hr.contract` with `hr.version`. Back-pay fields live on the version and are edited from the employee **Back Pay** tab (Payroll users).

## Install

1. Copy the `hr_back_pay` folder into your Odoo 19 addons path.
2. Update Apps list and install **HR Back Pay / Retroactive Pay**.
3. On install / upgrade, salary rules are added (or rewritten) on every payroll structure:
   - `ALW_RETROACTIVE`
   - `BACK_PAY_TAX`
   - `BACK_PAY_PENSION_7`
4. New payroll structures created later also receive these rules automatically.

## Usage

1. Open an **Employee**.
2. Open the **Back Pay** tab (Payroll users).
3. Set **Retroactive Months** and **Previous Net / Month** (or click **Fetch Last Slip**).
4. Review computed monthly difference, tax, and pension reporting amounts.
5. Click **Approve** (Finance Manager).
6. Generate the payslip — approved back pay is included as an untaxed allowance.

## Dependencies

- `hr`
- `hr_payroll`
- `mail`

## Upgrade from 18

1. Migrate the database to Odoo 19 with official scripts (contracts → versions).
2. Install / upgrade this module (`-u hr_back_pay`).
3. Salary-rule Python is rewritten from `contract.*` to `version.*` automatically.

## Note

Do **not** install this module together with Farm Management if both define the same version fields (`allowance_retroactive`, `back_pay_*`, etc.). Use either Farm Management’s built-in back pay **or** this standalone module.

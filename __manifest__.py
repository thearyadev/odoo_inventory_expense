{
    "name": "Business Expense Logger",
    "version": "18.0.1.0.0",
    "category": "Accounting/Expenses",
    "sequence": 25,
    "summary": "Log business expenses with categories, payment accounts, receipts, and reporting",
    "description": """
Business Expense Logger
=======================

This application allows staff to record general business expenses with
receipt uploads, category tracking, payment account tracking, and
date-based reporting.

Features:
---------
* Simple expense creation with receipt image upload
* Configurable hierarchical expense categories
* Configurable payment accounts with card/account metadata
* Track total amount and tax paid per expense
* Date-based filtering and reporting
* Excel export for expense reports
* PDF report generation
* Pivot table analysis by date periods
    """,
    "author": "Store Operations",
    "website": "",
    "license": "LGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/quick_add_wizard_views.xml",
        "views/business_expense_views.xml",
        "report/business_expense_report.xml",
        "wizard/expense_report_wizard_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "business_expense/static/src/scss/business_expense.scss",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}

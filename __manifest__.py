{
    "name": "Inventory Expense Logger",
    "version": "1.0.0",
    "category": "Inventory",
    "sequence": 25,
    "summary": "Log inventory purchase expenses with receipt tracking and reporting",
    "description": """
Inventory Expense Logger
========================

This application allows you to log basic inventory expenses from retailers
like Costco Business. Staff can record purchases with receipt uploads,
track total expenses and taxes, and generate date-based reports.

Features:
---------
* Simple expense creation with receipt image upload
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
        "views/inventory_expense_views.xml",
        "report/inventory_expense_report.xml",
        "wizard/expense_report_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "inventory_expense/static/src/scss/inventory_expense.scss",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}

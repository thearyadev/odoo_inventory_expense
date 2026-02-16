from odoo import api, models


class InventoryExpenseReport(models.AbstractModel):
    _name = "report.inventory_expense.report_inventory_expense"
    _description = "Inventory Expense Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["expense.report.wizard"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "expense.report.wizard",
            "docs": docs,
            "data": data,
        }

from odoo import api, models


class BusinessExpenseReport(models.AbstractModel):
    _name = "report.business_expense.report_business_expense"
    _description = "Business Expense Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["business.expense.report.wizard"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "business.expense.report.wizard",
            "docs": docs,
            "data": data,
        }

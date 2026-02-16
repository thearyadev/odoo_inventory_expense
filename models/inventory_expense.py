from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InventoryExpense(models.Model):
    _name = "inventory.expense"
    _description = "Inventory Expense"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Expense Name",
        required=True,
        tracking=True,
        help='Brief description of the expense (e.g., "Costco Business Center - Office Supplies")',
    )
    date = fields.Date(
        string="Expense Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True,
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        required=True,
        currency_field="currency_id",
        tracking=True,
        help="Total amount paid including tax",
    )
    tax_amount = fields.Monetary(
        string="Tax Amount",
        currency_field="currency_id",
        tracking=True,
        help="Tax portion of the total amount",
    )
    untaxed_amount = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_untaxed_amount",
        store=True,
        currency_field="currency_id",
        help="Total amount minus tax",
    )
    receipt_image = fields.Binary(
        string="Receipt Image",
        attachment=True,
        help="Upload a photo or scan of the receipt",
    )
    receipt_filename = fields.Char(
        string="Receipt Filename",
    )
    notes = fields.Text(
        string="Notes",
        help="Additional details about the expense",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="company_id.currency_id",
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True,
    )

    @api.depends("total_amount", "tax_amount")
    def _compute_untaxed_amount(self):
        for record in self:
            tax = record.tax_amount or 0.0
            record.untaxed_amount = record.total_amount - tax

    @api.constrains("total_amount", "tax_amount")
    def _check_amounts(self):
        for record in self:
            if record.total_amount < 0:
                raise ValidationError(_("Total amount cannot be negative."))
            if record.tax_amount and record.tax_amount < 0:
                raise ValidationError(_("Tax amount cannot be negative."))
            if record.tax_amount and record.tax_amount > record.total_amount:
                raise ValidationError(_("Tax amount cannot exceed total amount."))

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} - {record.date}"
            result.append((record.id, name))
        return result

    def action_view_report_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Expense Report",
            "res_model": "expense.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_date_from": self.date,
                "default_date_to": self.date,
            },
        }

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BusinessExpense(models.Model):
    _name = "business.expense"
    _description = "Business Expense"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    name = fields.Char(
        string="Expense Name",
        required=True,
        tracking=True,
        help='Brief description of the expense (e.g., "Costco Business Center - Supplies")',
    )
    category_id = fields.Many2one(
        comodel_name="business.expense.category",
        string="Category",
        required=True,
        index=True,
        ondelete="restrict",
        tracking=True,
    )
    account_id = fields.Many2one(
        comodel_name="business.expense.account",
        string="Payment Account",
        required=True,
        index=True,
        ondelete="restrict",
        tracking=True,
        check_company=True,
    )
    date = fields.Date(
        string="Expense Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True,
    )
    total_with_tax = fields.Monetary(
        string="Total Paid",
        required=True,
        currency_field="currency_id",
        tracking=True,
        help="Total amount paid at the register (including tax)",
    )
    total_without_tax = fields.Monetary(
        string="Subtotal",
        required=True,
        currency_field="currency_id",
        tracking=True,
        help="Amount before tax (subtotal on receipt)",
    )
    tax_amount = fields.Monetary(
        string="Tax Paid",
        compute="_compute_tax_amount",
        store=True,
        currency_field="currency_id",
        help="Tax amount (calculated from total - subtotal)",
    )
    total_amount = fields.Monetary(
        string="Total",
        compute="_compute_total_amount",
        store=True,
        currency_field="currency_id",
        help="Total amount (same as total paid)",
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
        index=True,
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
    is_zero_value = fields.Boolean(
        string="Zero Value",
        compute="_compute_is_zero_value",
        store=True,
        help="Indicates if the expense has a zero total amount",
    )
    needs_review = fields.Boolean(
        string="Needs Review",
        default=False,
        tracking=True,
        help="Indicates the expense data needs to be verified by a user",
    )

    @api.depends("total_with_tax")
    def _compute_is_zero_value(self):
        for record in self:
            record.is_zero_value = (
                record.total_with_tax == 0 or record.total_with_tax is False
            )

    @api.depends("total_with_tax", "total_without_tax")
    def _compute_tax_amount(self):
        for record in self:
            record.tax_amount = record.total_with_tax - record.total_without_tax

    @api.depends("total_with_tax")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.total_with_tax

    @api.constrains("total_with_tax", "total_without_tax")
    def _check_amounts(self):
        for record in self:
            if record.total_with_tax < 0:
                raise ValidationError(_("Total paid cannot be negative."))
            if record.total_without_tax < 0:
                raise ValidationError(_("Subtotal cannot be negative."))
            if record.total_without_tax > record.total_with_tax:
                raise ValidationError(_("Subtotal cannot exceed total paid."))

    @api.depends("name", "date")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} - {record.date}" if record.date else record.name

    def action_view_report_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Expense Report",
            "res_model": "business.expense.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_date_from": self.date,
                "default_date_to": self.date,
            },
        }

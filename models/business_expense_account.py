from odoo import api, fields, models


class BusinessExpenseAccount(models.Model):
    _name = "business.expense.account"
    _description = "Expense Payment Account"
    _rec_name = "name"
    _rec_names_search = ["name", "account_number", "account_holder"]
    _order = "account_holder, card_type, account_number"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    account_number = fields.Char(string="Account Number", required=True, index=True)
    card_type = fields.Selection(
        selection=[
            ("visa", "Visa"),
            ("mastercard", "Mastercard"),
            ("amex", "American Express"),
            ("discover", "Discover"),
            ("debit", "Debit Card"),
            ("bank", "Bank Account"),
            ("cash", "Cash"),
            ("check", "Check"),
            ("other", "Other"),
        ],
        string="Card Type",
        required=True,
        default="visa",
    )
    account_holder = fields.Char(string="Account Holder", required=True, index=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "account_number_company_uniq",
            "unique(account_number, company_id)",
            "An expense payment account with this account number already exists for this company.",
        ),
    ]

    def _get_masked_account_number(self):
        self.ensure_one()
        account_number = self.account_number or ""
        digits = "".join(character for character in account_number if character.isdigit())
        if len(digits) >= 4:
            return "ending %s" % digits[-4:]
        return account_number

    @api.depends("account_number", "card_type", "account_holder")
    def _compute_name(self):
        for account in self:
            card_type = dict(account._fields["card_type"].selection).get(account.card_type, "Account")
            parts = [card_type]
            if account.account_number:
                parts.append(account._get_masked_account_number())
            if account.account_holder:
                parts.append(account.account_holder)
            account.name = " - ".join(parts)

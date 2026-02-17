from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openai_model = fields.Char(
        string="OpenAI Model",
        config_parameter="inventory_expense.openai_model",
        default="gpt-4o-mini",
        help="The OpenAI model to use for receipt extraction (e.g., gpt-4o-mini, gpt-4o)",
    )

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BusinessExpenseCategory(models.Model):
    _name = "business.expense.category"
    _description = "Expense Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "sequence, complete_name"

    name = fields.Char(string="Category Name", required=True, translate=True, index=True)
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )
    parent_id = fields.Many2one(
        comodel_name="business.expense.category",
        string="Parent Category",
        index=True,
        ondelete="cascade",
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        comodel_name="business.expense.category",
        inverse_name="parent_id",
        string="Child Categories",
    )
    sequence = fields.Integer(default=10)
    color = fields.Integer(string="Color", default=0)
    active = fields.Boolean(default=True)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = "%s / %s" % (
                    category.parent_id.complete_name,
                    category.name,
                )
            else:
                category.complete_name = category.name

    @api.constrains("parent_id")
    def _check_category_recursion(self):
        if self._has_cycle():
            raise ValidationError(_("You cannot create recursive expense categories."))

    @api.model
    def name_create(self, name):
        category = self.create({"name": name})
        return category.id, category.display_name

    @api.depends_context("hierarchical_naming")
    def _compute_display_name(self):
        if self.env.context.get("hierarchical_naming", True):
            return super()._compute_display_name()
        for category in self:
            category.display_name = category.name

import json
import logging
import os
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_EXTRACTION_PROMPT = """Extract the following information from this receipt image:
1. vendor_name: The store or vendor name (e.g., "Costco Business Center", "Walmart")
2. date: The transaction date in YYYY-MM-DD format (use the date on the receipt, or leave null if not found)
3. subtotal: The amount before tax (the subtotal line on the receipt)
4. total: The final amount paid including tax

Be precise with the numbers. If you cannot clearly read a value, set it to null.
Return the result as a JSON object with these exact keys: vendor_name, date, subtotal, total."""


class QuickAddWizard(models.TransientModel):
    _name = "quick.add.wizard"
    _description = "Quick Add Expense Wizard"

    receipt_file = fields.Binary(
        string="Receipt File",
        required=True,
        help="Upload a receipt image (JPG, PNG) or PDF",
    )
    receipt_filename = fields.Char(
        string="Filename",
    )

    def _get_mime_type(self):
        if self.receipt_filename:
            ext = self.receipt_filename.lower().split(".")[-1]
            mime_map = {
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "gif": "image/gif",
                "webp": "image/webp",
                "pdf": "application/pdf",
            }
            return mime_map.get(ext, "image/jpeg")
        return "image/jpeg"

    def _get_openai_client(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise UserError(
                _("OpenAI library is not installed. Please contact your administrator.")
            )

        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1")

        if not api_key:
            raise UserError(
                _(
                    "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
                )
            )

        return OpenAI(api_key=api_key, base_url=base_url)

    def _get_config(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        return {
            "model": get_param("inventory_expense.openai_model", default="gpt-4o-mini"),
            "prompt": DEFAULT_EXTRACTION_PROMPT,
        }

    def _extract_with_ai(self):
        self.ensure_one()

        client = self._get_openai_client()
        config = self._get_config()
        mime_type = self._get_mime_type()

        file_data = self.receipt_file
        if isinstance(file_data, bytes):
            file_data = file_data.decode("utf-8")
        image_url = f"data:{mime_type};base64,{file_data}"

        try:
            response = client.chat.completions.create(
                model=config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": config["prompt"],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high",
                                },
                            }
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
            )

            content = response.choices[0].message.content
            if not content:
                return None

            data = json.loads(content)
            return {
                "vendor_name": data.get("vendor_name"),
                "date": data.get("date"),
                "subtotal": data.get("subtotal"),
                "total": data.get("total"),
            }

        except json.JSONDecodeError as e:
            _logger.warning("Failed to parse AI response as JSON: %s", e)
            return None
        except Exception as e:
            _logger.error("AI extraction failed: %s", e)
            return None

    def _create_expense(
        self, name, date=None, subtotal=None, total=None, needs_review=False
    ):
        today = fields.Date.context_today(self)

        if date:
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                parsed_date = today
        else:
            parsed_date = today

        expense = self.env["inventory.expense"].create(
            {
                "name": name,
                "date": parsed_date,
                "total_without_tax": subtotal if subtotal is not None else 0.0,
                "total_with_tax": total if total is not None else 0.0,
                "receipt_image": self.receipt_file,
                "receipt_filename": self.receipt_filename,
                "needs_review": needs_review,
            }
        )
        return expense

    def action_quick_add(self):
        self.ensure_one()

        if not self.receipt_file:
            raise UserError(_("Please upload a receipt file."))

        today = fields.Date.context_today(self)
        name = f"Quick Add - {today}"

        expense = self._create_expense(name=name)

        return {
            "type": "ir.actions.act_window",
            "name": _("Expense Created"),
            "res_model": "inventory.expense",
            "res_id": expense.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_quick_add_ai(self):
        self.ensure_one()

        if not self.receipt_file:
            raise UserError(_("Please upload a receipt file."))

        extraction = self._extract_with_ai()
        today = fields.Date.context_today(self)

        if extraction:
            vendor_name = extraction.get("vendor_name") or f"Quick Add - {today}"
            date = extraction.get("date")
            subtotal = extraction.get("subtotal")
            total = extraction.get("total")

            if subtotal is None:
                subtotal = 0.0
            if total is None:
                total = 0.0

            expense = self._create_expense(
                name=vendor_name,
                date=date,
                subtotal=subtotal,
                total=total,
                needs_review=True,
            )

            return {
                "type": "ir.actions.act_window",
                "name": _("Expense Created"),
                "res_model": "inventory.expense",
                "res_id": expense.id,
                "view_mode": "form",
                "target": "current",
            }
        else:
            name = f"Quick Add - {today}"
            expense = self._create_expense(name=name)

            return {
                "type": "ir.actions.act_window",
                "name": _("Expense Created"),
                "res_model": "inventory.expense",
                "res_id": expense.id,
                "view_mode": "form",
                "target": "current",
                "context": {
                    "default_message": _(
                        "AI extraction failed. Created expense with generic name. Please review and update manually."
                    )
                },
            }

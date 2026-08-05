import odoo.tests.common as common
from odoo import Command, fields


class TestAccountUXChangeCurrency(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.today = fields.Date.today()
        self.company_usd = self.env.ref("base.main_company")

        # Sin datos demo la compañía puede no tener plan de cuentas; lo cargamos si hace falta.
        if not self.env["account.account"].search_count([("company_id", "=", self.company_usd.id)]):
            self.env["account.chart.template"].try_loading(False, company=self.company_usd)

        self.partner = self.env["res.partner"].create({"name": "Test Partner Account UX"})

        self.currency_usd = self.env.ref("base.USD")
        self.currency_ars = self.env.ref("base.ARS")
        self.currency_ars.write({"active": True})

        self.product = self.env["product.product"].create(
            {"name": "Test Product Account UX", "list_price": 1000.0}
        )

        self.journal_usd = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.company_usd.id)], limit=1
        )

        self.journal_ars = self.journal_usd.copy()

        self.journal_ars.write({"currency_id": self.currency_ars})

    def test_account_ux_change_currency(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "date": self.today,
                "move_type": "out_invoice",
                "journal_id": self.journal_usd.id,
                "company_id": self.company_usd.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 1000,
                        }
                    ),
                ],
            }
        )

        invoice.write({"journal_id": self.journal_ars.id})

        invoice.action_post()

        self.assertEqual(
            invoice.currency_id,
            self.journal_ars.currency_id,
            "La moneda de la factura no está siendo modificada al cambiar el diario.",
        )

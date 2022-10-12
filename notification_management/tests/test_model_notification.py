from odoo.tests.common import TransactionCase
import uuid


class TestModelNotification(TransactionCase):

    def test_notify_by_value(self):
        unique_message = uuid.uuid4()
        self._create_notification('sale.order.line', 'quantity', unique_message)
        self._create_sale(self.product1, '2022-01-01', quantity=101)
        email = self.env['email.notification'].search([('message', '=', unique_message)])
        self.assertEqual(len(email), 1)

    def _create_notification(self, model_name, field_name, message):
        model = self.env[model_name]
        field = getattr(model, field_name)
        notification = self.env['notification.compare.value'].create({
            'name': 'Notification by value 10',
            'model_id': model.id,
            'field_id': field.id,
            'operator': '>',
            'threshold_type': 'amount',
            'threshold_value': 0,
            'message': message,
            'notification_type': 'email',
            'reference_value': 100,
            'filter_domain': '[]',
            'model_name': 'sale.order.line'
        })
        return notification

    @classmethod
    def setUpClass(cls):
        super(TestModelNotification, cls).setUpClass()
        cls.product1 = cls.env['product.product'].create({
            'name': 'product1',
            'type': 'consu',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'default_code': 'XXXXXXXXXXXXXXXXXXXXXXX',
            'detailed_type': 'consu',
            'sale_line_warn': 'no-message'
        })
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Partner A',
            'country_id': cls.env['res.country'].create({
                'name': 'Country A',
                'code': 'ZZ',
            }).id,
            'vat': 'AA123456789',
        })
        cls.currency_data = cls.setup_multi_currency_data()
        cls.env.ref('base.EUR').active = True

    def _create_sale(self, product, date, quantity=1.0):
        rslt = self.env['sale.order'].create({
            'partner_id': self.partner_a.id,
            'currency_id': self.currency_data['currency'].id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': quantity,
                    'product_uom': product.uom_po_id.id,
                    'price_unit': 66.0,
                })],
            'date_order': date,
        })
        rslt.action_confirm()
        return rslt

    @classmethod
    def setup_multi_currency_data(cls, default_values=None, rate2016=3.0, rate2017=2.0):
        default_values = default_values or {}
        foreign_currency = cls.env['res.currency'].create({
            'name': 'Gold Coin',
            'symbol': '☺',
            'rounding': 0.001,
            'position': 'after',
            'currency_unit_label': 'Gold',
            'currency_subunit_label': 'Silver',
            **default_values,
        })
        rate1 = cls.env['res.currency.rate'].create({
            'name': '2016-01-01',
            'rate': rate2016,
            'currency_id': foreign_currency.id,
            'company_id': cls.env.company.id,
        })
        rate2 = cls.env['res.currency.rate'].create({
            'name': '2017-01-01',
            'rate': rate2017,
            'currency_id': foreign_currency.id,
            'company_id': cls.env.company.id,
        })
        return {
            'currency': foreign_currency,
            'rates': rate1 + rate2,
        }

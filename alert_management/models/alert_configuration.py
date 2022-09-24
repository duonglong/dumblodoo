from odoo import models, api, fields, _

OPERATORS = [
    ('eq', '='),
    ('gt', '>'),
    ('lt', '<'),
    ('ge', '>='),
    ('le', '<='),
]

THRESHOLD_TYPE = [
    ('amount', 'Amount'),
    ('percentage', 'Percentage')
]

ALERT_TYPE = [
    ('email', 'Email')
]

class AlertConfiguration(models.Model):
    _name = 'alert.configuration'

    name = fields.Char(string=_("Name"), required=True)
    model_id = fields.Many2one(string=_("Object"), comodel_name='ir.model')
    field_id = fields.Many2one(string=_("Field"), comodel_name="ir.model.fields")
    operator = fields.Selection(string=_("Operator"), selection=OPERATORS, default='gt')
    threshold_type = fields.Selection(string=_("Threshold Type"), selection=THRESHOLD_TYPE, default='percentage')
    threshold_value = fields.Float(string=_("Threshold"))
    message = fields.Html('Contents', render_engine='qweb', compute=False, default='', sanitize_style=True)
    receiver_ids = fields.Many2many(string=_("Receivers"), comodel_name='res.partner')
    alert_type = fields.Selection(selection=ALERT_TYPE, default='email', required=1)
    active = fields.Boolean(default=True)
    compared_field

    def send_alert(self):
        alerter = self.env['alert.sender.factory'].get_alerter(self)
        alerter.send_message()

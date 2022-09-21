from odoo import models, api, fields, _

OPERATORS = [
    ('=', '='),
    ('>', '>'),
    ('<', '<'),
    ('>=', '>='),
    ('<=', '<='),
]

THRESHOLD_TYPE = [
    ('amount', 'Amount'),
    ('percentage', 'Percentage')
]


class AlertConfiguration(models.Model):
    _name = 'alert.configuration'

    name = fields.Char(string=_("Name"), required=True)
    model_id = fields.Many2one(string=_("Object"), comodel_name='ir.model')
    left_field_id = fields.Many2one(string=_("Left"), comodel_name="ir.model.fields")
    right_field_id = fields.Many2one(string=_("Right"), comodel_name="ir.model.fields")
    operator = fields.Selection(string=_("Operator"), selection=OPERATORS)
    threshold_type = fields.Selection(string=_("Threshold Type"), selection=THRESHOLD_TYPE)
    threshold_value = fields.Float(string=_("Threshold"))

    def _send_alert(self):
        pass

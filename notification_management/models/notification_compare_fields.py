from odoo import models, api, fields, _


class NotificationCompareFields(models.Model):
    _name = 'notification.compare.fields'
    _inherits = {'notification.configuration': 'noti_config_id'}

    CRITICAL_FIELDS = [
        'model_id',
        'field_id',
        'operator',
        'threshold_type',
        'threshold_value',
        'comparable_field_id'
    ]

    noti_config_id = fields.Many2one(string=_("Notification Config"), comodel_name='notification.configuration')
    comparable_field_id = fields.Many2one(string=_("Field"), comodel_name="ir.model.fields")

    def check_condition(self, record):
        field_value = getattr(record, self.field_id.name)
        comparable_field_value = getattr(record, self.comparable_field_id.name)
        if self.threshold_type == 'amount':
            value = field_value - comparable_field_value
        else:
            value = (field_value / comparable_field_value) * 100
        expression = self.get_comparison_expression(value)
        return eval(expression)
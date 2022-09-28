from odoo import models, api, fields, _


class NotificationCompareValue(models.Model):
    _name = 'notification.compare.value'
    _inherits = {'notification.configuration': 'noti_config_id'}

    CRITICAL_FIELDS = [
        'model_id',
        'field_id',
        'operator',
        'threshold_type',
        'threshold_value',
        'reference_value'
    ]

    noti_config_id = fields.Many2one(string=_("Notification Config"), comodel_name='notification.configuration')
    reference_value = fields.Float(string=_("Reference Value"))

    def check_condition(self, record):
        field_value = getattr(record, self.field_id.name)
        if self.threshold_type == 'amount':
            value = field_value - self.reference_value
        else:
            value = (field_value / self.reference_value) * 100
        expression = self.get_comparison_expression(value)
        return eval(expression)


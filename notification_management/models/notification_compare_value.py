from odoo import models, api, fields, _


class NotificationCompareValue(models.Model):
    _name = 'notification.compare.value'
    _inherit = 'notification.configuration'

    CRITICAL_FIELDS = [
        'model_id',
        'field_id',
        'operator',
        'threshold_type',
        'threshold_value',
        'reference_value'
    ]

    reference_value = fields.Float(string=_("Reference Value"))

    def _get_comparable_value(self, record):
        return self.reference_value

    def _register_hook(self):
        self.register_hook(self._name)

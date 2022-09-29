from odoo import models, api, fields, _


class NotificationCompareFields(models.Model):
    _name = 'notification.compare.fields'
    _inherit = 'notification.configuration'

    CRITICAL_FIELDS = [
        'model_id',
        'field_id',
        'operator',
        'threshold_type',
        'threshold_value',
        'comparable_field_id'
    ]

    comparable_field_id = fields.Many2one(string=_("Comparable Field"), comodel_name="ir.model.fields")

    def get_comparable_value(self, record):
        return getattr(record, self.comparable_field_id.name)

    @api.onchange('model_id')
    def onchange_model_id(self):
        super().onchange_model_id()
        self.comparable_field_id = [fields.Command.clear()]

    def _register_hook(self):
        self.register_hook(self._name)
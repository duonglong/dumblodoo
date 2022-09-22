from odoo import models, fields


class AlertSenderFactory(models.AbstractModel):
    _name = 'alert.sender.factory'

    alert_config_id = fields.Many2one(comodel_name="alert.configuration")

    def get_all_senders(self):
        return {
            'email': self.env['email.alert']
        }

    def get_alerter(self):
        senders = self.get_all_senders()
        alerter = senders.get(self.alert_config_id.alert_type, None)
        if alerter:
            values = self.get_alerter_values()
            alerter = alerter.create(values)
            return alerter
        return self.env['alert.sender']

    def get_alerter_values(self):
        return {
            'message': self.alert_config_id.message,
            'partner_ids': [(6, 0, self.alert_config_id.partner_ids.ids)]
        }

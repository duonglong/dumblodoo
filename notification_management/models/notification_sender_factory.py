from odoo import models, fields


class NotificationSenderFactory(models.AbstractModel):
    _name = 'notification.sender.factory'

    notification_config_id = fields.Many2one(comodel_name="notification.configuration")

    def get_all_senders(self):
        return {
            'email': self.env['email.notification']
        }

    def get_notificationer(self):
        senders = self.get_all_senders()
        notificationer = senders.get(self.notification_config_id.notification_type, None)
        if notificationer:
            values = self.get_notificationer_values()
            notificationer = notificationer.create(values)
            return notificationer
        return self.env['notification.sender']

    def get_notificationer_values(self):
        return {
            'message': self.notification_config_id.message,
            'partner_ids': [(6, 0, self.notification_config_id.partner_ids.ids)]
        }

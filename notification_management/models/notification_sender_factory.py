from odoo import models, fields, api


class NotificationSenderFactory(models.AbstractModel):
    _name = 'notification.sender.factory'

    notification_config_id = None

    def get_all_senders(self):
        return {
            'email': self.env['email.notification']
        }

    @api.model
    def get_sender(self, config):
        senders = self.get_all_senders()
        sender_obj = senders.get(config.notification_type, None)
        if sender_obj is not None:
            values = self._get_sender_values(config)
            return sender_obj.create(values)
        return self.env['notification.sender']

    @api.model
    def _get_sender_values(self, config):
        return {
            'message': config.message,
            'receiver_ids': [(6, 0, config.receiver_ids.ids)]
        }

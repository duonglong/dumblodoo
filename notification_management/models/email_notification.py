from odoo import models, api, fields, _


class EmailNotification(models.Model):
    _name = 'email.notification'
    _inherit = ['notification.sender', 'mail.thread']

    def send_message(self):
        self.message_post(body=self.message)
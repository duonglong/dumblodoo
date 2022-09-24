from odoo import models, api, fields, _


class EmailAlert(models.Model):
    _name = 'email.alert'
    _inherit = ['alert.sender', 'mail.thread']

    def send_message(self):
        self.message_post(body=self.message)
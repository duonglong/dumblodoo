from odoo import models, api, fields, _


class EmailNotification(models.Model):
    _name = 'email.notification'
    _inherit = ['notification.sender', 'mail.thread']

    def send_message(self):
        vals = {
            'subject': '[NOTIFICATION] Test',
            'body_html': self.message,
            'author_id': self.env.user.partner_id.id,
            'email_from': self.env.user.email_formatted,
            'email_to': ','.join([receiver.email for receiver in self.receiver_ids]),
            'auto_delete': False,
        }

        mail_id = self.env['mail.mail'].sudo().create(vals)
        mail_id.sudo().send()
        self.message_post(body=self.message)
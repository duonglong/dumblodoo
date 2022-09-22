from odoo import models, api, fields, _



class AlertSender(models.AbstractModel):
    _name = 'alert.sender'

    message = fields.Html('Contents', render_engine='qweb', compute=False, default='', sanitize_style=True)
    partner_ids = fields.Many2many(string=_("Partner"), comodel_name='res.partner')

    def send_message(self):
        raise _("Send message is not implemented")
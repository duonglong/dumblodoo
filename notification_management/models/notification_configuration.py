from odoo import models, api, fields, _
from collections import defaultdict
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


OPERATORS = [
    ('==', '='),
    ('>', '>'),
    ('<', '<'),
    ('>=', '>='),
    ('<=', '<='),
]

THRESHOLD_TYPE = [
    ('amount', 'Amount'),
    ('percentage', 'Percentage')
]

ALERT_TYPE = [
    ('email', 'Email')
]

class NotificationConfiguration(models.AbstractModel):
    _name = 'notification.configuration'

    CRITICAL_FIELDS = [
        'model_id',
        'field_id',
        'operator',
        'threshold_type',
        'threshold_value',
    ]

    name = fields.Char(string=_("Name"), required=True)
    model_id = fields.Many2one(string=_("Object"), comodel_name='ir.model')
    field_id = fields.Many2one(string=_("Field"), comodel_name="ir.model.fields")
    operator = fields.Selection(string=_("Operator"), selection=OPERATORS, default='=')
    threshold_type = fields.Selection(string=_("Threshold Type"), selection=THRESHOLD_TYPE, default='percentage')
    threshold_value = fields.Float(string=_("Threshold"))
    message = fields.Html('Contents', render_engine='qweb', compute=False, default='', sanitize_style=True)
    receiver_ids = fields.Many2many(string=_("Receivers"), comodel_name='res.partner')
    notification_type = fields.Selection(selection=ALERT_TYPE, default='email', required=1)
    active = fields.Boolean(default=True)

    def send_notification(self):
        messenger = self.env['notification.sender.factory'].get_sender(self)
        messenger.send_message()

    def check_condition(self, record):
        raise ValidationError(_("Check condition wasn't implemented"))

    def get_comparison_expression(self, value):
        return "{value} {operator} {threshold_value}".format(
            value=value,
            operator=self.operator,
            threshold_value=self.threshold_value
        )

    def check_and_send_notification(self, records):
        if self.check_condition(records):
            self.send_notification()

    def get_model_configurations(self, records):
        model_name = records._name
        return self.search([('model_id.model', '=', model_name)])

    def check_condition(self, record):
        value = self.get_condition_value(record, self.get_comparable_value(record))
        expression = self.get_comparison_expression(value)
        return eval(expression)

    def get_comparable_value(self, record):
        raise ValidationError(_("Get comparable Value is not implemented"))

    def get_condition_value(self, record, compare_value):
        field_value = getattr(record, self.field_id.name)
        if self.threshold_type == 'amount':
            value = field_value - compare_value
        else:
            value = (field_value / self.reference_value) * 100 if self.reference_value > 0 else 0
        return value

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.field_id = [fields.Command.clear()]

    @api.model_create_multi
    def create(self, vals_list):
        patcher = super(NotificationConfiguration, self).create(vals_list)
        self._update_registry()
        return patcher

    def write(self, vals):
        res = super(NotificationConfiguration, self).write(vals)
        if set(vals).intersection(self.CRITICAL_FIELDS):
            self._update_registry()
        return res

    def unlink(self):
        res = super(NotificationConfiguration, self).unlink()
        self._update_registry()
        return res

    def _update_registry(self):
        """ Update the registry after a modification on action rules. """
        if self.env.registry.ready and not self.env.context.get('import_file'):
            # re-install the model patches, and notify other workers
            self._unregister_hook()
            self._register_hook()
            self.env.registry.registry_invalidated = True

    def register_hook(self, config_model_name):
        """ Patch models that should trigger action rules based on creation,
            modification, deletion of records and form onchanges.
        """
        #
        # Note: the patched methods must be defined inside another function,
        # otherwise their closure may be wrong. For instance, the function
        # create refers to the outer variable 'create', which you expect to be
        # bound to create itself. But that expectation is wrong if create is
        # defined inside a loop; in that case, the variable 'create' is bound to
        # the last function defined by the loop.
        #

        def make_create():
            """ Instanciate a create method that processes action rules. """

            @api.model_create_multi
            def create(self, vals_list, **kw):
                # call original method
                records = create.origin(self.with_env(self.env), vals_list, **kw)
                notifications = self.env[config_model_name].get_model_configurations(records)
                if notifications:
                    notifications.check_and_send_notification(records)
                return records.with_env(self.env)

            return create

        def make_write():
            """ Instanciate a write method that processes action rules. """
            def write(self, vals, **kw):
                write.origin(self.with_env(self.env), vals, **kw)

                notifications = self.env[config_model_name].get_model_configurations(self)
                if notifications:
                    notifications.check_and_send_notification(self)
                return True

            return write

        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`, unless it has been patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve all actions, and patch their corresponding model
        for config in self.with_context({}).search([]):
            model_name = config.model_id.model
            Model = self.env.get(model_name)

            # Do not crash if the model of the base_action_rule was uninstalled
            if Model is None:
                _logger.warning("Action rule with ID %d depends on model %s" %
                                (config.id,
                                model_name))
                continue

            patch(Model, 'create', make_create())
            patch(Model, 'write', make_write())

    def _unregister_hook(self):
        """ Remove the patches installed by _register_hook() """
        NAMES = ['create', 'write', '_compute_field_value']
        for Model in self.env.registry.values():
            for name in NAMES:
                try:
                    delattr(Model, name)
                except AttributeError:
                    pass

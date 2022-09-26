from odoo import models, api, fields, _
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


OPERATORS = [
    ('eq', '='),
    ('gt', '>'),
    ('lt', '<'),
    ('ge', '>='),
    ('le', '<='),
]

THRESHOLD_TYPE = [
    ('amount', 'Amount'),
    ('percentage', 'Percentage')
]

ALERT_TYPE = [
    ('email', 'Email')
]

class AlertConfiguration(models.Model):
    _name = 'alert.configuration'

    name = fields.Char(string=_("Name"), required=True)
    model_id = fields.Many2one(string=_("Object"), comodel_name='ir.model')
    field_id = fields.Many2one(string=_("Field"), comodel_name="ir.model.fields")
    operator = fields.Selection(string=_("Operator"), selection=OPERATORS, default='gt')
    threshold_type = fields.Selection(string=_("Threshold Type"), selection=THRESHOLD_TYPE, default='percentage')
    threshold_value = fields.Float(string=_("Threshold"))
    reference_value = fields.Float(string=_("Reference Value"))
    message = fields.Html('Contents', render_engine='qweb', compute=False, default='', sanitize_style=True)
    receiver_ids = fields.Many2many(string=_("Receivers"), comodel_name='res.partner')
    alert_type = fields.Selection(selection=ALERT_TYPE, default='email', required=1)
    active = fields.Boolean(default=True)
    comparable_field_id = fields.Many2one(string=_("Field"), comodel_name="ir.model.fields")
    compare_between_fields = fields.Boolean(string=_("Compare between 2 fields"), default=False)

    def send_alert(self):
        alerter = self.env['alert.sender.factory'].get_alerter(self)
        alerter.send_message()

    def check_condition(self, record):
        field_value = getattr(record, self.field_id.name)
        comparable_field_value = 0
        if self.comparable_field_id:
           comparable_field_value = getattr(record, self.comparable_field_id.name)

        value = field_value - comparable_field_value

    def check_and_send_alert(self, records):
        pass


    def get_model_configurations(self, records):
        model_name = records._name
        return self.search([('model_id.name', '=', model_name)])


    CRITICAL_FIELDS = [
        'model_id',
        'field_id',
        'operator',
        'threshold_type',
        'threshold_value',
        'comparable_field_id'
    ]

    @api.model_create_multi
    def create(self, vals_list):
        patcher = super(AlertConfiguration, self).create(vals_list)
        self._update_registry()
        return patcher

    def write(self, vals):
        res = super(AlertConfiguration, self).write(vals)
        if set(vals).intersection(self.CRITICAL_FIELDS):
            self._update_registry()
        return res

    def unlink(self):
        res = super(AlertConfiguration, self).unlink()
        self._update_registry()
        return res

    def _update_registry(self):
        """ Update the registry after a modification on action rules. """
        if self.env.registry.ready and not self.env.context.get('import_file'):
            # re-install the model patches, and notify other workers
            self._unregister_hook()
            self._register_hook()
            self.env.registry.registry_invalidated = True

    def _register_hook(self):
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
                alerts = self.env['alert.configuration'].get_model_configurations(records)
                if alerts:
                    alerts.check_and_send_alert(records)
                return records.with_env(self.env)

            return create

        def make_write():
            """ Instanciate a write method that processes action rules. """

            def write(self, vals, **kw):
                write.origin(self.with_env(self.env), vals, **kw)

                alerts = self.env['alert.configuration'].get_model_configurations(self)
                if alerts:
                    alerts.check_and_send_alert(self)
                return True

            return write

        def make_compute_field_value():
            """ Instanciate a compute_field_value method that processes action rules. """

            #
            # Note: This is to catch updates made by field recomputations.
            #
            def _compute_field_value(self, field):
                # determine fields that may trigger an action
                stored_fields = [f for f in self.pool.field_computed[field] if f.store]
                if not any(stored_fields):
                    return _compute_field_value.origin(self, field)
                # retrieve the action rules to possibly execute
                alerts = self.env['alert.configuration'].get_model_configurations(self)
                records = self.filtered('id').with_env(alerts.env)
                if not (alerts and records):
                    _compute_field_value.origin(self, field)
                    return True

                # call original method
                _compute_field_value.origin(self, field)
                # check postconditions, and execute actions on the records that satisfy them
                alerts.check_and_send_alert(self)
                return True

            return _compute_field_value


        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`, unless it has been patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve all actions, and patch their corresponding model
        for action_rule in self.with_context({}).search([]):
            Model = self.env.get(action_rule.model_name)

            # Do not crash if the model of the base_action_rule was uninstalled
            if Model is None:
                _logger.warning("Action rule with ID %d depends on model %s" %
                                (action_rule.id,
                                 action_rule.model_name))
                continue

            patch(Model, 'create', make_create())
            patch(Model, 'write', make_write())
            patch(Model, '_compute_field_value', make_compute_field_value())

    def _unregister_hook(self):
        """ Remove the patches installed by _register_hook() """
        NAMES = ['create', 'write', '_compute_field_value']
        for Model in self.env.registry.values():
            for name in NAMES:
                try:
                    delattr(Model, name)
                except AttributeError:
                    pass

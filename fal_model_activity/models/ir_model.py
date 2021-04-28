from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import pycompat


class IrModel(models.Model):
    _inherit = 'ir.model'

    fal_is_mail_activity = fields.Boolean(
        string="Mail Activity", default=False,
        help="Whether this model supports activities.",
    )

    @api.multi
    def write(self, vals):
        if self and 'fal_is_mail_activity' in vals:
            if not all(rec.state == 'manual' for rec in self):
                raise UserError(_('Only custom models can be modified.'))
            if not all(rec.fal_is_mail_activity <= vals['fal_is_mail_activity'] for rec in self):
                raise UserError(_('Field "Mail Activity" cannot be changed to "False".'))
            res = super(IrModel, self).write(vals)
            # setup models; this reloads custom models in registry
            self.pool.setup_models(self._cr)
            # update database schema of models
            models = self.pool.descendants(self.mapped('model'), '_inherits')
            self.pool.init_models(self._cr, models, dict(self._context, update_custom_fields=True))
        else:
            res = super(IrModel, self).write(vals)
        return res

    def _reflect_model_params(self, model):
        vals = super(IrModel, self)._reflect_model_params(model)
        vals['fal_is_mail_activity'] = issubclass(type(model), self.pool['mail.activity.mixin'])
        return vals

    @api.model
    def _instanciate(self, model_data):
        model_class = super(IrModel, self)._instanciate(model_data)
        
        parents = model_class._inherit or []
        parents = [parents] if isinstance(parents, pycompat.string_types) else parents
        
        if model_data.get('fal_is_mail_activity') and model_class._name != 'mail.activity.mixin':
            parents = parents + ['mail.activity.mixin']
        
        model_class._inherit = parents
        
        return model_class
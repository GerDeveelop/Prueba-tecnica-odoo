from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ItAssetRequest(models.Model):
    _name = 'it.asset.request'
    _description = 'IT Asset Request'
    # Heredamos mail.thread y mail.activity.mixin para tener el historial (chatter) nativo en Odoo
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Campos requeridos por la prueba técnica
    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_name = fields.Char(string='Nombre del Empleado', required=True, tracking=True)
    employee_email = fields.Char(string='Email')
    request_date = fields.Date(string='Fecha de Solicitud', default=fields.Date.context_today)
    
    asset_type = fields.Selection([
        ('laptop', 'Laptop'),
        ('monitor', 'Monitor'),
        ('teclado', 'Teclado'),
        ('mouse', 'Mouse'),
        ('licencia', 'Licencia de software')
    ], string='Tipo de Activo', required=True, tracking=True)
    
    justification = fields.Text(string='Justificación')
    priority = fields.Selection([
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta')
    ], string='Prioridad', default='media')
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Enviado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft', tracking=True)
    
    approved_by = fields.Many2one('res.users', string='Aprobado por', readonly=True)
    approval_date = fields.Datetime(string='Fecha de Aprobación', readonly=True)
    is_urgent = fields.Boolean(string='Es Urgente')
    estimated_cost = fields.Float(string='Costo Estimado')
    
    # Campos de adjuntos explícitamente solicitados en el documento Word
    attachment = fields.Binary(string='Adjunto')
    attachment_name = fields.Char(string='Nombre del Adjunto')
    
    # Campo calculado para mostrar información resumida
    display_name_info = fields.Char(string='Info de Solicitud', compute='_compute_display_name_info', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribimos el método create para asignar automáticamente la secuencia 
        configurada en data/sequence.xml cuando se crea un nuevo registro.
        """
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('it.asset.request') or _('New')
        return super().create(vals_list)

    @api.depends('asset_type', 'employee_name', 'priority')
    def _compute_display_name_info(self):
        """
        Calcula un string informativo basado en el tipo de activo, empleado y prioridad.
        """
        for record in self:
            if record.asset_type and record.employee_name and record.priority:
                record.display_name_info = f"{dict(record._fields['asset_type'].selection).get(record.asset_type)} - {record.employee_name} - {record.priority.capitalize()}"
            else:
                record.display_name_info = ""

    @api.onchange('asset_type')
    def _onchange_asset_type(self):
        """
        Marca automáticamente la solicitud como urgente si se selecciona una Laptop o Licencia.
        """
        if self.asset_type in ['laptop', 'licencia']:
            self.is_urgent = True
        else:
            self.is_urgent = False

    @api.constrains('estimated_cost')
    def _check_estimated_cost(self):
        """
        Valida que el usuario no pueda ingresar valores negativos en el costo estimado.
        """
        for record in self:
            if record.estimated_cost < 0:
                raise ValidationError(_("El costo estimado no puede ser negativo."))

    # --- MÉTODOS DE TRANSICIÓN DE ESTADO ---
    
    def action_submit(self):
        """Transición a estado 'Enviado'"""
        self.write({'state': 'submitted'})

    def action_approve(self):
        """
        Transición a estado 'Aprobado'.
        Valida que esté en 'submitted' y guarda el usuario que aprueba y la fecha actual.
        """
        for record in self:
            if record.state != 'submitted':
                raise ValidationError(_("Solo se pueden aprobar solicitudes en estado 'Enviado'."))
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approval_date': fields.Datetime.now()
            })

    def action_reject(self):
        """
        Transición a estado 'Rechazado'.
        Valida que esté en estado 'submitted' antes de rechazar.
        """
        for record in self:
            if record.state != 'submitted':
                raise ValidationError(_("Solo se pueden rechazar solicitudes en estado 'Enviado'."))
            record.write({'state': 'rejected'})
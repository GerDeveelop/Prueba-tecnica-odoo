# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ItAssetRequest(models.Model):
    """
    Gestiona el ciclo de vida de las solicitudes de activos tecnológicos.
    Hereda de mail.thread para auditoría y mail.activity.mixin para gestión de tareas.
    """
    _name = 'it.asset.request'
    _description = 'Solicitud de Activos TI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # --- Campos de Identificación ---
    name = fields.Char(
        string='Referencia', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('Nuevo')
    )
    
    # --- Relaciones y Datos del Solicitante ---
    employee_id = fields.Many2one(
        'res.partner', 
        string='Solicitante', 
        required=True, 
        tracking=True,
        help="Persona o empleado que requiere el activo."
    )
    employee_email = fields.Char(
        related='employee_id.email', 
        string='Email Corporativo', 
        store=True,
        readonly=True
    )
    
    # --- Detalles del Activo ---
    request_date = fields.Date(
        string='Fecha de Solicitud', 
        default=fields.Date.context_today,
        readonly=True
    )
    asset_type = fields.Selection([
        ('laptop', 'Laptop'),
        ('monitor', 'Monitor'),
        ('teclado', 'Teclado'),
        ('mouse', 'Mouse'),
        ('licencia', 'Licencia de software')
    ], string='Tipo de Activo', required=True, tracking=True)
    
    priority = fields.Selection([
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta')
    ], string='Prioridad', default='media', tracking=True)

    # --- Gestión de Costos y Estado ---
    estimated_cost = fields.Float(
        string='Costo Estimado',
        help="Valor aproximado del activo solicitado."
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Enviado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Estado', default='draft', tracking=True)

    # --- Datos de Aprobación ---
    approved_by = fields.Many2one('res.users', string='Aprobado por', readonly=True)
    approval_date = fields.Datetime(string='Fecha de Aprobación', readonly=True)
    
    # --- Información Adicional ---
    justification = fields.Text(string='Justificación')
    is_urgent = fields.Boolean(string='Es Urgente', help="Indica si el activo requiere prioridad inmediata.")
    attachment = fields.Binary(string='Documento Adjunto')
    attachment_name = fields.Char(string='Nombre del Archivo')
    
    display_name_info = fields.Char(
        string='Información Resumida', 
        compute='_compute_display_name_info', 
        store=True
    )

    # --- Lógica Computada y Eventos ---

    @api.model_create_multi
    def create(self, vals_list):
        """ Asignación de secuencia automática al crear el registro. """
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('it.asset.request') or _('Nuevo')
        return super(ItAssetRequest, self).create(vals_list)

    @api.depends('asset_type', 'employee_id', 'priority')
    def _compute_display_name_info(self):
        """ Genera una etiqueta descriptiva para facilitar la búsqueda visual. """
        for record in self:
            if record.asset_type and record.employee_id:
                type_label = dict(self._fields['asset_type'].selection).get(record.asset_type)
                record.display_name_info = f"{type_label} - {record.employee_id.name}"

    @api.onchange('asset_type')
    def _onchange_asset_type(self):
        """ Lógica proactiva: las laptops y licencias se marcan como urgentes por defecto. """
        self.is_urgent = self.asset_type in ['laptop', 'licencia']

    @api.constrains('estimated_cost')
    def _check_estimated_cost(self):
        """ Validación de integridad de datos financieros. """
        for record in self:
            if record.estimated_cost < 0:
                raise ValidationError(_("El costo estimado no puede ser un valor negativo."))

    # --- Acciones de Workflow ---

    def action_submit(self):
        """ Pasa la solicitud a revisión por parte del equipo de TI. """
        self.ensure_one()
        self.write({'state': 'submitted'})

    def action_approve(self):
        """ Finaliza la solicitud registrando auditoría del aprobador. """
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })

    def action_reject(self):
        """ Marca la solicitud como rechazada. """
        self.write({'state': 'rejected'})
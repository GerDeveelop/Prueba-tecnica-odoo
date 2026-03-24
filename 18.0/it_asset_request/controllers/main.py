# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class AssetRequestController(http.Controller):
    """
    Controlador encargado de la exposición del servicio en el sitio web.
    Maneja la creación y visualización de solicitudes desde el frontend.
    """

    @http.route('/asset-request', type='http', auth='public', website=True)
    def asset_request_form(self, **kw):
        """ Renderiza el formulario de captura de datos para el usuario final. """
        return request.render('it_asset_request.asset_request_form_template', {})

    @http.route('/asset-request/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def asset_request_submit(self, **post):
        """
        Procesa el envío del formulario. 
        Implementa lógica de búsqueda de contactos para evitar duplicidad de registros.
        """
        name = post.get('employee_name')
        email = post.get('email')
        
        # Uso de sudo() para permitir que usuarios públicos (sin login) guarden datos
        Partner = request.env['res.partner'].sudo()
        partner = Partner.search([('email', '=', email)], limit=1) if email else False
            
        if not partner:
            partner = Partner.create({
                'name': name, 
                'email': email, 
                'company_type': 'person'
            })

        # Creación del registro vinculado al contacto encontrado o creado
        request_val = {
            'employee_id': partner.id,
            'asset_type': post.get('asset_type'),
            'justification': post.get('justification'),
            'priority': post.get('priority', 'media'),
            'estimated_cost': float(post.get('estimated_cost', 0.0)),
            'state': 'submitted'
        }
        
        new_request = request.env['it.asset.request'].sudo().create(request_val)
        
        # Redirección dinámica a la vista de éxito/detalle
        return request.redirect(f'/asset-request/{new_request.id}')

    @http.route('/asset-request/<int:request_id>', type='http', auth='public', website=True)
    def asset_request_detail(self, request_id, **kw):
        """ Muestra un resumen de la solicitud procesada para confirmación del usuario. """
        asset_req = request.env['it.asset.request'].sudo().browse(request_id)
        if not asset_req.exists():
            return request.not_found()
            
        return request.render('it_asset_request.asset_request_detail_template', {
            'asset_request': asset_req
        })
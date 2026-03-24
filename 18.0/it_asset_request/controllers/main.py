from odoo import http
from odoo.http import request

class AssetRequestController(http.Controller):

    # Ruta 1: Muestra el formulario web. auth='public' permite acceso sin login.
    @http.route('/asset-request', type='http', auth='public', website=True)
    def asset_request_form(self, **kw):
        return request.render('it_asset_request.asset_request_form_template', {})

    # Ruta 2: Recibe los datos por POST y crea la solicitud.
    @http.route('/asset-request/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def asset_request_submit(self, **post):
        # Mapeamos los datos del formulario a los campos del modelo
        request_val = {
            'employee_name': post.get('employee_name'),
            'employee_email': post.get('email'),
            'asset_type': post.get('asset_type'),
            'justification': post.get('justification'),
            'priority': post.get('priority', 'media'),
            'estimated_cost': float(post.get('estimated_cost', 0.0)),
            'state': 'submitted' # Estado requerido al enviar desde la web
        }
        # sudo() es obligatorio aquí porque un usuario público no tiene permisos de escritura nativos
        new_request = request.env['it.asset.request'].sudo().create(request_val)
        
        # Redirigimos a la página de detalle usando el ID generado
        return request.redirect(f'/asset-request/{new_request.id}')

    # Ruta 3: Muestra el detalle de una solicitud específica.
    @http.route('/asset-request/<int:request_id>', type='http', auth='public', website=True)
    def asset_request_detail(self, request_id, **kw):
        # Buscamos el registro con sudo() por si el usuario no tiene sesión iniciada
        asset_req = request.env['it.asset.request'].sudo().browse(request_id)
        if not asset_req.exists():
            return request.not_found()
            
        return request.render('it_asset_request.asset_request_detail_template', {
            'asset_request': asset_req
        })
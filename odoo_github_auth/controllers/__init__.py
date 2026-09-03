from odoo import http, fields
from odoo.http import request, jsonify
import logging
import json

_logger = logging.getLogger(__name__)


class GithubAuthController(http.Controller):
    """GitHub OAuth Authentication Controller"""

    @http.route('/auth/github/login', type='http', auth='public', website=True)
    def github_login(self, **kwargs):
        """Redirect to GitHub authorization"""
        provider = request.env['github.oauth.provider'].search(
            [('is_active', '=', True)],
            limit=1
        )
        
        if not provider:
            return request.render('web.login', {
                'error': 'GitHub authentication is not configured'
            })

        # Generate authorization URL
        auth_url = (
            f"{provider.authorize_url}?"
            f"client_id={provider.client_id}&"
            f"redirect_uri={provider.redirect_uri}&"
            f"scope={provider.scope}&"
            f"state=github_auth"
        )
        
        return request.redirect(auth_url)

    @http.route('/auth/github/callback', type='http', auth='public')
    def github_callback(self, code=None, state=None, error=None, **kwargs):
        """Handle GitHub OAuth callback"""
        if error:
            _logger.warning(f"GitHub auth error: {error}")
            return request.redirect('/web/login?error=GitHub authorization failed')

        if not code:
            return request.redirect('/web/login?error=No authorization code received')

        try:
            provider = request.env['github.oauth.provider'].search(
                [('is_active', '=', True)],
                limit=1
            )
            
            if not provider:
                raise Exception('GitHub provider not configured')

            # Exchange code for access token
            access_token = provider.get_access_token(code)
            
            # Get user information
            github_info = provider.get_user_info(access_token)
            
            # Create or update user
            user = request.env['res.users'].sudo().create_from_github(
                github_info,
                access_token
            )
            
            # Log the user in
            request.env.cr.commit()
            request.session.authenticate(request.session.db, user.login, 'github_oauth')
            
            return request.redirect('/web')
            
        except Exception as e:
            _logger.error(f"GitHub callback error: {str(e)}")
            return request.redirect(f'/web/login?error={str(e)}')

    @http.route('/webhook/github', type='json', auth='public', csrf=False)
    def github_webhook(self, **kwargs):
        """Handle GitHub webhook events"""
        try:
            # Verify webhook signature
            signature = request.httprequest.headers.get('X-Hub-Signature-256')
            event_type = request.httprequest.headers.get('X-GitHub-Event')
            
            payload = request.jsonrequest
            
            # Create webhook record
            webhook = request.env['github.webhook'].sudo().create({
                'event_type': event_type or 'push',
                'payload': payload,
                'status': 'pending',
            })
            
            # Process webhook asynchronously
            webhook.with_delay().process_webhook()
            
            return jsonify({'status': 'received'})
            
        except Exception as e:
            _logger.error(f"Webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 400

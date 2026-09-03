import requests
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GithubOAuthProvider(models.Model):
    """GitHub OAuth Provider Configuration"""
    _name = 'github.oauth.provider'
    _description = 'GitHub OAuth Provider'

    name = fields.Char('GitHub App Name', required=True)
    client_id = fields.Char('Client ID', required=True)
    client_secret = fields.Char('Client Secret', required=True, password=True)
    redirect_uri = fields.Char('Redirect URI', compute='_compute_redirect_uri')
    scope = fields.Char('Scopes', default='user:email read:org')
    is_active = fields.Boolean('Active', default=True)
    
    authorize_url = fields.Char(
        'Authorization URL',
        default='https://github.com/login/oauth/authorize'
    )
    token_url = fields.Char(
        'Token URL',
        default='https://github.com/login/oauth/access_token'
    )
    userinfo_url = fields.Char(
        'User Info URL',
        default='https://api.github.com/user'
    )

    @api.depends('name')
    def _compute_redirect_uri(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url'
        )
        for record in self:
            record.redirect_uri = f"{base_url}/auth/github/callback"

    def get_access_token(self, code):
        """Exchange authorization code for access token"""
        try:
            response = requests.post(
                self.token_url,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                },
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.RequestException as e:
            _logger.error(f"GitHub token exchange failed: {str(e)}")
            raise UserError(_('Failed to authenticate with GitHub'))

    def get_user_info(self, access_token):
        """Get user information from GitHub"""
        try:
            response = requests.get(
                self.userinfo_url,
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f"GitHub user info retrieval failed: {str(e)}")
            raise UserError(_('Failed to retrieve GitHub user information'))


class GithubWebhook(models.Model):
    """GitHub Webhook Handler"""
    _name = 'github.webhook'
    _description = 'GitHub Webhook Events'

    event_type = fields.Selection([
        ('push', 'Push Event'),
        ('pull_request', 'Pull Request'),
        ('issues', 'Issues'),
        ('release', 'Release'),
        ('repository', 'Repository'),
    ], required=True)
    
    payload = fields.Json('Webhook Payload')
    timestamp = fields.Datetime('Event Timestamp', default=fields.Datetime.now)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ], default='pending')
    error_message = fields.Text('Error Message')

    def process_webhook(self):
        """Process GitHub webhook event"""
        for record in self:
            try:
                if record.event_type == 'push':
                    record._handle_push_event()
                elif record.event_type == 'pull_request':
                    record._handle_pull_request()
                elif record.event_type == 'issues':
                    record._handle_issues()
                record.status = 'processed'
            except Exception as e:
                record.status = 'failed'
                record.error_message = str(e)
                _logger.error(f"Webhook processing failed: {str(e)}")

    def _handle_push_event(self):
        """Handle push events"""
        payload = self.payload
        repo_name = payload.get('repository', {}).get('name')
        branch = payload.get('ref', '').split('/')[-1]
        _logger.info(f"Push to {repo_name}:{branch}")

    def _handle_pull_request(self):
        """Handle pull request events"""
        payload = self.payload
        action = payload.get('action')
        pr_number = payload.get('pull_request', {}).get('number')
        _logger.info(f"Pull request {action}: #{pr_number}")

    def _handle_issues(self):
        """Handle issue events"""
        payload = self.payload
        action = payload.get('action')
        issue_number = payload.get('issue', {}).get('number')
        _logger.info(f"Issue {action}: #{issue_number}")


class ResUsers(models.Model):
    """Extend res.users for GitHub integration"""
    _inherit = 'res.users'

    github_login = fields.Char('GitHub Login', unique=True)
    github_id = fields.Char('GitHub User ID', unique=True)
    github_avatar_url = fields.Char('GitHub Avatar URL')
    github_profile_url = fields.Char('GitHub Profile URL')
    github_email = fields.Char('GitHub Email')
    github_company = fields.Char('GitHub Company')
    github_location = fields.Char('GitHub Location')
    github_bio = fields.Text('GitHub Bio')
    github_access_token = fields.Char('GitHub Access Token', password=True)
    github_sync_date = fields.Datetime('Last GitHub Sync')

    @api.model
    def create_from_github(self, github_info, access_token):
        """Create or update user from GitHub information"""
        github_login = github_info.get('login')
        github_id = github_info.get('id')
        email = github_info.get('email')

        # Check if user exists
        user = self.search([
            '|',
            ('github_login', '=', github_login),
            ('github_id', '=', str(github_id))
        ], limit=1)

        user_vals = {
            'login': email or github_login,
            'email': email or f"{github_login}@github.local",
            'name': github_info.get('name') or github_login,
            'github_login': github_login,
            'github_id': str(github_id),
            'github_avatar_url': github_info.get('avatar_url'),
            'github_profile_url': github_info.get('html_url'),
            'github_email': email,
            'github_company': github_info.get('company'),
            'github_location': github_info.get('location'),
            'github_bio': github_info.get('bio'),
            'github_access_token': access_token,
            'github_sync_date': fields.Datetime.now(),
        }

        if user:
            user.write(user_vals)
        else:
            user = self.create(user_vals)

        return user

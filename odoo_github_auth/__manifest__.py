# Odoo 19 GitHub Authentication Module
# OAuth 2.0 + SSO + Webhooks Integration

{
    'name': 'GitHub Authentication',
    'version': '19.0.1.0.0',
    'category': 'Authentication',
    'summary': 'GitHub OAuth 2.0, SSO and Webhooks Integration',
    'author': 'Odoo Dev Team',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'auth_oauth'],
    'external_dependencies': {
        'python': ['requests', 'PyJWT'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/github_oauth_views.xml',
        'views/github_webhook_views.xml',
        'views/res_users_views.xml',
        'data/github_oauth_provider.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_cryptocurrency',
        'odoo14-addon-currency_monthly_rate',
        'odoo14-addon-currency_old_rate_notify',
        'odoo14-addon-currency_rate_inverted',
        'odoo14-addon-currency_rate_update',
        'odoo14-addon-currency_rate_update_cmc',
        'odoo14-addon-currency_rate_update_transferwise',
        'odoo14-addon-currency_rate_update_xe',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)

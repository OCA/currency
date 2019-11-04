import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-currency_monthly_rate',
        'odoo12-addon-currency_rate_inverted',
        'odoo12-addon-currency_rate_update',
        'odoo12-addon-currency_rate_update_oxr',
        'odoo12-addon-currency_rate_update_transferwise',
        'odoo12-addon-currency_rate_update_xe',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)

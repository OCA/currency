import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_cryptocurrency',
        'odoo11-addon-account_fx_spot',
        'odoo11-addon-currency_monthly_rate',
        'odoo11-addon-currency_rate_inverted',
        'odoo11-addon-currency_rate_update',
        'odoo11-addon-currency_rate_update_cmc',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)

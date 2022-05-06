import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_cryptocurrency',
        'odoo14-addon-currency_rate_inverted',
        'odoo14-addon-currency_rate_update',
        'odoo14-addon-currency_rate_update_cmc',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)

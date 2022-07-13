import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-currency_rate_inverted',
        'odoo13-addon-currency_rate_update',
        'odoo13-addon-currency_rate_update_transferwise',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)

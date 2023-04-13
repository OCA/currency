import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-currency_rate_update>=15.0dev,<15.1dev',
        'odoo-addon-currency_rate_update_xe>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)

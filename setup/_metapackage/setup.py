import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-currency",
    description="Meta package for oca-currency Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-currency_old_rate_notify>=16.0dev,<16.1dev',
        'odoo-addon-currency_rate_update>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)

from setuptools import setup

setup(
    name='Clienvix',
    version='1.0',
    description='Gestiona la consulta al API de navixy para ver listas de clientes, cuentas y trackers',
    author='Steven Garcia',
    author_email='ing.sgarcia13@gmail.com',
    packages=['modulos'], install_requires=['requests 2.32.5', 'pandas 3.0.1', 'openpyxl 3.1.5', 'setuptools 82.0.0'],
)

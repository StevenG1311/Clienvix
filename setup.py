from setuptools import setup

setup(
    name='Clienvix',
    version='1.4.0',
    description='Gestiona la consulta al API de navixy para ver listas de clientes, datos de las cuentas y trackers',
    author='Steven Garcia',
    author_email='ing.sgarcia13@gmail.com',
    packages=['modulos'], install_requires=[
        'requests 2.32.5',
        'pandas 3.0.1',
        'openpyxl 3.1.5',
        'pwinput 1.0.3',
        'tqdm 4.67.3',
        'setuptools 82.0.0']
)

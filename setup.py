from setuptools import setup

setup(
    name='social',
    packages=['social'],
    include_package_data=True,
    version="0.0.1",
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'mysqlclient',
        'sqlalchemy==1.2.10',
        'flask-restful',
        'requests',
        'itsdangerous',
        'bcrypt',
        'marshmallow',
        'pycryptodome',
        'gunicorn',
        "simplejson"
    ],
)
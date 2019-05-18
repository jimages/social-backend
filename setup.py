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
        'SQLAlchemy>=1.3.0',
        'flask-restful',
        'requests',
        'flask-redis',
        'redis',
        'itsdangerous',
        'bcrypt',
        'marshmallow',
        'pycryptodome',
        'gunicorn',
        "simplejson"
    ],
)
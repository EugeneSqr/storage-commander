from setuptools import setup

setup(
    name='storcom',
    version='0.0.1',
    py_modules=['storage_commander'],
    install_requires=[
        'Click', 'requests',
    ],
    entry_points={
        'console_scripts': [
            'storcom = storage_commander:storcom',
        ],
    },
)

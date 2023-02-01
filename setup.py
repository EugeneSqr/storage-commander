from setuptools import setup, find_packages

setup(
    name='storcom',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'Click', 'requests', 'tomli', 'tabulate', 'curlify',
    ],
    entry_points={
        'console_scripts': [
            'storcom = storcom.storage_commander:storcom',
        ],
    },
)

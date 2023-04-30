from setuptools import setup, find_packages

setup(
    name='storcom',
    version='0.0.1',
    python_requires='>=3.7',
    packages=find_packages(),
    install_requires=[
        'Click', 'requests', 'tomli', 'tabulate', 'curlify', 'python-dateutil',
    ],
    entry_points={
        'console_scripts': [
            'storcom = storcom.storage_commander:storcom',
        ],
    },
)

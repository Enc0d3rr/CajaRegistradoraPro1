# setup.py
from setuptools import setup, find_packages
import sys

# Leer requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="caja-registradora",
    version="1.0.0",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'caja-registradora=main:main',
        ],
    },
)

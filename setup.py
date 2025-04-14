# Always prefer setuptools over distutils
# To use a consistent encoding
from codecs import open
from os import path

from setuptools import setup

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="LayerAkiraSDK",
    version="1.0.0a90",
    description="library for interaction with LayerAkira exchange",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LayerAkira/python_akira",
    author="Garrancha",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent"
    ],
    packages=["LayerAkira", "LayerAkira.src", "LayerAkira.src.common", "LayerAkira.executables",
              "LayerAkira.src.hasher", "LayerAkira.src.sor"],
    include_package_data=True,
    install_requires=[
        'websockets',
        'toml',
        'starknet-py>=0.22.0',
        'requests',
        'aioconsole>=0.7.0'
    ]
)
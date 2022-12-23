"""
Kaki setup
==========
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from kaki import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="kaki",
    version=__version__,
    description="Kivy application library on steroids",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tito/kaki",
    author="Mathieu Virbel",
    author_email="mat@meltingrocks.com",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["kivy", "watchdog"],
    project_urls={
        "Bug Reports": "https://github.com/tito/kaki/issues",
        "Source": "https://github.com/tito/kaki/",
    },
)

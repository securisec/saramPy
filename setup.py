from setuptools import setup, find_packages
from os import path

__version__ = '1.1.1'
__author__ = 'Hapsida @securisec'

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    long_description=long_description,
    long_description_content_type='text/markdown',
    name="saramPy",
    version=__version__,
    author=__author__,
    packages=find_packages(),
    install_requires = [
        'requests',
        'delegator.py'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7"
    ],
    entry_points={
        'console_scripts': [
            'saram = saramPy.__main__:main'
        ]
    }
)

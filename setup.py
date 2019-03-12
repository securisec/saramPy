from setuptools import setup, find_packages
from saram import __version__, __author__

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name="saram",
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
            'saram = saram.__main__:main'
        ]
    }
)

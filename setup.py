from setuptools import setup, find_packages
from paramduni import __version__, __author__

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name="paramduni",
    version=__version__,
    author=__author__,
    packages=find_packages(),
    install_requires = read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3.7"
    ],
    entry_points={
        'console_scripts': [
            'paramduni = paramduni.__main__:main'
        ]
    }
)

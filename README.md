<img src="https://raw.githubusercontent.com/securisec/saramPy/master/logo.png" width="150px">

[![Build Status](https://travis-ci.com/securisec/saramPy.svg?token=8GQfGnTK7S1NU7bKCqeR&branch=master)](https://travis-ci.com/securisec/saramPy)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](http://sarampy.readthedocs.io/en/latest/)

# saramPy
`saramPy` is the Python bindings for the Saram API. It provides both a Python module to be used from Python scripts, and also a command line util called `saram`.

## Requirements
`saramPy` is written and works only with **Python 3.7+**


## Install
May have to install with *sudo* to ensure saram is placed on path. 
```bash
pip3 install saramPy
```

#### Install dev version with pip
```
git clone https://github.com/securisec/saramPy.git
cd saramPy
pip3 install -e .
# to update future versions without reinstalling, use from inside saramPy folder
git pull
```

## Usage
### Script
Refer to the docs on how to user `saramPy` Python module.

### Command line tool
```bash
$ saram --help
usage: saram [-h] -t TOKEN -u SLACK_USER [-l] [--comment COMMENT]
             [-c ... | -f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Token provided in Slack
  -u SLACK_USER, --user SLACK_USER
                        Slack username
  -l, --local           Dev mode. Use localhost
  --comment COMMENT     Add an optional comment
  -c ..., --command ...
                        Command to run inside quotes
  -f FILE, --file FILE  Read a file and send it to the server
```


## Docs 

[Documentation is on readthedocs](http://sarampy.readthedocs.io/en/latest/)

To manually set up docs, run the following commands from inside the 
saram directory
```
pip3 install sphinx
cd docs/
make clean html
```

Then open the docs located in `_build/html/index.html`

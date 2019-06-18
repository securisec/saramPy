Saram's documentation
=====================

.. image:: logo.png
    :width: 200

This is the documentation for saramPy, the Python interface for the Saram API.

Usage
=====
saramPy uses two tokens to communicate with the Saram server. 
One of them is the API token, and one of them is the entry token. Although both of the tokens are required, the API token can be read from a local config file. This config file is in JSON format and contains the API key and the username associated with that API key. This config file can be set up in two ways:

Python
""""""

.. code-block:: python

    from saramPy import SaramInit
    s = SaramInit(api_key='yourApiKey')
    s.init()

Command line
""""""""""""

.. code-block:: bash

    saramPy --init yourApiKey [--base_url] [--local]
    # Set --local to set self hosted solution, or --base_url if using anything other than the main app

saramPy docs
""""""""""""

Command line tool
=================
```saramPy``` will install a handy command line tool that ties around the most commonly used methods and send them to the server. 

.. code-block:: bash

    usage: saramPy [-h] -t TOKEN [--comment COMMENT] [-c ... | -f FILE]

    optional arguments:
    -h, --help            show this help message and exit
    -t TOKEN, --token TOKEN
                            Token for the entry
    --comment COMMENT     Add an optional comment
    -c ..., --command ...
                            Command to run inside quotes
    -f FILE, --file FILE  Read a file and send it to the server

Python module
=============
```saramPy``` exposes two main classes with distinct use cases.

saramPy.Saram
"""""""""""""
This class exposes the most helpful classes and is typically used for:
    
    - sending script output
    - sending command output
    - sending code examples

.. autoclass:: saramPy.Saram
    :members:

saramPy.api.SaramAPI
""""""""""""""""""""
This class exports the full functionality of the Saram API and can be 
use to build tools and integrations around.

`API docs <https://py.saram.io>`__

.. autoclass:: saramPy.api.SaramAPI
    :members:

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

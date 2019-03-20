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

    saram --init yourApiKey

saramPy docs
""""""""""""

.. automodule:: saramPy
    :members:

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

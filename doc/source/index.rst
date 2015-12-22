.. Cinfdata Database Client documentation master file, created by
   sphinx-quickstart on Tue Dec 22 08:28:16 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the documentation for the Cinfdata Database Client!
==============================================================

Cinfdata Client is a simple Python module for accessing and caching data from the Cinfdata
database. The use of the module could look something like this::

    from cinfdata import Cinfdata
    from matplotlib import pyplot as plt

    # Instantiate the database client for a specific setup e.g. stm312
    db = Cinfdata('stm312')
    # Get the data and metadata for a specific id
    spectrum = db.get_data(6688)
    metadata = db.get_metadata(6688)

    plt.plot(spectrum[:,0], spectrum[:, 1])
    plt.title(metadata['Comment'])
    plt.show()

To get started, please start by reading the first few sections of the
:ref:`introduction`. Then have a look at the :ref:`examples` or the :ref:`api`.

Contents
========

.. toctree::
   :maxdepth: 2

   introduction
   examples
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


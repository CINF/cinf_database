.. Cinfdata Database Client documentation master file, created by
   sphinx-quickstart on Tue Dec 22 08:28:16 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Cinfdata Database Client's documentation!
====================================================

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

To get started please start by reading the short :ref:`introduction`. It contains some
important information about the dangers of locally caching data that is worth reading
**before** starting to use the module. After this, dive into one of the :ref:`examples`,
that aims to covers all the different ways the module can be used. If you need detailed
information about the calling signature of methods etc. have a look in the :ref:`api`.


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


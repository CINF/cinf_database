.. _examples:

Examples
========

.. _simplest-example:

Simplest Possible Example
-------------------------

This examples contains a detailed explanation of the simplest possible
example. Many of the following examples will build of this one.

.. code-block:: python

    from cinfdata import Cinfdata
    cinfdb = Cinfdata('stm312')
    data = cinfdb.get_data(6688)
    metadata = cinfdb.get_metadata(6688)

* Line 1 imports the cinfdata module. For this to be possible, it must
  be in your Python path (which is the list of folders that Python can
  import from). The simplest way to do that is to simple drop the
  cinfdata.py file in the same folder as your data treatment script.
* Line 2 makes a **Cinf**\ data **d**\ ata\ **b**\ ase client object,
  abbreviated cinfdb\ [#shortnames]_. The only mandatory
  argument to the :py:class:`~cinfdata.Cinfdata` class is the codename
  of the setup in this case `'stm312'`.
* Line 3 fetches the data ...

  .. code-block:: text

      array([[  1.56250000e-02,   2.09650000e-13],
             [  3.12500000e-02,   1.86725000e-13],
             [  4.68750000e-02,   1.58958000e-13],
             ...,
             [  9.99687500e+01,   7.48633000e-14],
             [  9.99843750e+01,   6.37814000e-14],
             [  1.00000000e+02,   7.38152000e-14]])

* Line 4 fetches the metadata as a dictionary ...

  .. code-block:: python

      {'Comment': 'Chamber background,P=9.7E-11torr', 'pass_energy': None, 'pre_wait_time': None,
       'timestep': None, 'year': None, 'file_name': None, 'preamp_range': 0, 'project': None,
       'number_of_scans': None, 'mass_label': 'Mass Scan', 'actual_mass': None,
       'SEM_voltage': 2200.0, u'unixtime': 1418807588L,
       'time': datetime.datetime(2014, 12, 17, 10, 13, 8), 'excitation_energy': None, 'type': 4L,
       'id': 6688L, 'name': None}

Simple Example with Plot
------------------------

`Code <https://github.com/CINF/cinf_database/blob/master/examples/simple_with_plot.py>`_

To make a plot that uses e.g. the `comment` fielde of the metadata as
the title, :ref:`simplest-example` can be expanded into::

  from cinfdata import Cinfdata
  from matplotlib import pyplot as plt

  db = Cinfdata('stm312')
  spectrum = db.get_data(6688)
  metadata = db.get_metadata(6688)

  plt.plot(spectrum[:, 0], spectrum[:, 1])
  plt.title(metadata['Comment'])
  plt.show()

.. note:: The data comes out the same way in would if it was fetched
          directly from the database i.e. with x and y being two
          columns in a numpy array, so they are retrieved individually
          with the `[:, 0]` syntax

Simple Example Using the Cache
------------------------------

`Code <https://github.com/CINF/cinf_database/blob/master/examples/simple_with_cache.py>`_

To enable caching of the database results (which is disabled by
default) simply instantiate the :class:`Cinfdata` object with
`use_caching=True`::

  from cinfdata import Cinfdata

  db = Cinfdata('stm312', use_caching=True)
  spectrum = db.get_data(6688)
  metadata = db.get_metadata(6688)

Except from the instantiation argument, the usage is exactly the
same. If the folder of the cinfdata.py file, there will now be a cache
folder with the following content::

  cache
  └── stm312
      ├── data
      │   └── 6688.npy
      └── infoitem.pickle

A folder for each of the setups being used (``stm312`` in this
case). Under that, there is the ``data`` folder, that contains one
file (named ``meaurement_id.npy``\ [#npy]_) for each data set and
there is the infoitem.pickle ([#pickle]) that contains all the
metadata.

.. important:: Due to the use of native data saving functionality and
               the use of pickle, the cache **cannot** be used across
               different operating systems or Pythons versions. Only
               use on **one** machine and **one** Python version. If
               you need to switch machines or Python version you
               shoule reset the cache.

To reset the cache simply delete the cache folder.

.. rubric:: Footnotes

.. [#shortnames] In general, Python users are encouraged to make
                 descriptive variable names, which often means that
                 they should be written fully out to make the code
                 easier to read. However, it is "allowed" to make **a
                 few** very short variables, if they are used
                 extremely often (like it is often done with Numpy as
                 np, Pyplot as plt etc.). Besides, cinfdb, is close to
                 readable, 'db' is a common abbreaviation for database
                 and all readers should know what Cinf is.
.. [#npy] npy is numpys own save format for arrays. It it very
          efficient because it contains just a small header, that
          contains the array dimensions and the data type and then
          just the raw bytes that describes the numbers.
.. [#pickle] pickle is Python serialization format for serialization
             of (almost) arbitrary arguments. The format is not
             guarantied to be preserved across Python version, which
             is one of the reasons that the cache should not be used
             across Python versions.

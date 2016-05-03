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

Simple example with plot
------------------------



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

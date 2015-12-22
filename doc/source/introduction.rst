.. _introduction:

Introduction
============

This pages provides an introduction to using the Cinfdate Database Client. Please read at
least this sections and the :ref:`dangers-of-caching` section before jumping in with the
:ref:`examples`. The rest of the sections are optional background.

The Cinfdata Database Client has three main goals:

1. To provide a **easy-to-use interface** to the data in the Cinfdata database
2. To **get rid of lot of copied, nearly identical, code snippets** that is present in a
   lot of peoples data treatment scrips (see :ref:`getting-rid-of-copied-code` for
   details)
3. To **enable local caching** of the data returned by the Cinfdata database, in order to
   speed up fetching the data and make it possible to work offline or of poor internet
   connections

Goals 1 and 2 are achieved mainly by making the maximum number of assumptions possible
about:

a. The structure of the database (which **should always** be correct™)
b. The setup of the users data treament enviroment (which is correct most of the time, or can be
   adjusted)

It is important to know this, because if your local environment (e.g. the port
number you for the port forward for database access) is not the same as what most people
use, then you will have to change it or provide the client with the information.


Goal 3 is an sought after improvement over the way that most people use the Cinfdata
database today. The local caching functionality will save both data and metadata, that has
previously been retrieved from the database, in files. The next time the same information
is requested, it will be returned from the cache instead. The advantages to this are:

a. This will completely elliminate the need to ask the database to collect the correct
   data, to transfer it over the network and put in the form of a numpy array (data
   case). Therefore, it will provide a significant speed-up\ [#f1]_ in the time it
   takes to get the data.
b. Local caching will also make it possible to work off-line or of a poor internet
   connection

There are however also downsides to caching. The most important of these is the risk of
getting out of sync with your data (please read section :ref:`dangers-of-caching` for
details). Of less importance is the space the data will takeup on your local harddrive.

.. _dangers-of-caching:

Dangers of Caching
------------------

This section is called "Dangers of Caching", which is a bit of an overstatement. But it is
important to understand how caching works, in order to understand the limitations.

In general, caching of data is essentially the idea of putting a temporary storage *in
between* the source of the data and the destination. This cache will be closer to the
destination and therefore be quicker.

One big advantage to this idea (besides the speed up) is that the storage is temporary. A
local cache can always be deleted witout worrying about loosing data.

But this idea puts an extra layer of complexity to the structure of getting the data that
has a few side effects that it is important to be aware of.

.. important:: The cache can get out of date

The most important property of caching, to be aware of, is that it can **go out of
date**. The cache in the Cinfdata Database Client is based on the ids of the
measurements. This means that the first time the data for a specific id is requested, it
will be fetched from the database and cached, but all subsequent times it is requested,
the cached version will be returned.

This means that if more data is added to the dataset, after the first time it is requested
(this could be the case for long running measurements), the client will not show the
changes but simply keep returning the incomplete 'old' version of the data.

**This client makes no attempt to try and check whether the data is up-to-date**, or to
make it possible to update the cache. If you think that you are seeing incomplete data,
simply delete the cache and start over.

Another problem, more specific to this client, is that the column names of the metadata
table is also cached the first time the client is used. This means that if columns are
added to the metadata table, the new columns will never be shown. Once again, the only
option is to delete the cache and start over.


That is it for the warnings. If you are eager to get started head over to the
:ref:`examples`. If you want a bit more background, then read on.

.. _getting-rid-of-copied-code:

Getting Rid of Copied Code
--------------------------

Manually copying and pasting code around is error prone and annoying. Therefore, we should
always strive to get rid of repetition. For data treatment scripts, especially 2 pieces of
code are present in a lot of different script: Database connection code and helper
functions for retrieving data.

The Cinfdate database is only available of the local network, so to access it e.g. from
home, it is necessary to set up a port forward. This means that when the database
connection is made it will be necessary to detect that it fails to make the direct
connetion and try the port forward. This translates roughly into code like this::

    try:
        connection = MySQLdb.connect(host='servcinf', user=username,
                                     passwd=password, db='cinfdata')
    except CONNECT_EXCEPTION:
        try:
            connection = MySQLdb.connect('localhost', port=9999, user=username,
	                                 passwd=password, db='cinfdata')
        except CONNECT_EXCEPTION:
            raise Exception('No database connection')

While this works, it is not exactly simple to read and understand, and it is annoying to
have to keep this around the start of all data treatment scripts.

For retriving data, some will probably have written little helper functions like e.g::

    def get_data(dataid):
        """Get data from the database"""
        query = 'SELECT x, y FROM xy_values_dummy WHERE measurement=%s'
	cursor.execute(query, [dataid])
	all_rows = cursor.fetchall()
	return np.array(all_rows)

Which may get more complicated to get the metadata.

Both of these common pieces of code is included directly in the Cinfdata Database
Client. The means that getting setup to get data and fetching a single dataset is reduced
to just one line of code each. See the :ref:`examples` for details on how to use it.


.. rubric:: Footnotes

.. [#f1] The exact speed-up is difficuly to quantify, because the databaser server (MySQL)
         in itself will also cache frequently requested data. A few simple tests suggests
         a >30x speed up, even with frequently requested data. What is however much more
         important that the absolute size of the speed-up, is that this (for most data
         treatment scripts) should mean that getting the data is no longer a significant
         fraction of the total run-time of the script.

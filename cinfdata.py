# pylint: disable=no-member,import-error,invalid-name,too-many-instance-attributes
# pylint: disable=too-many-arguments

"""Convinience interface to the cinfdata database"""

from __future__ import unicode_literals, print_function

from os import path
import os
import sys
from time import time
import cPickle
import logging
from collections import namedtuple

import numpy as np


# Set up logging
logging.basicConfig(format='%(name)s: %(message)s', level=logging.INFO)
LOG = logging.getLogger('CINFDATA')


# First try and import MySQLdb ..
try:
    import MySQLdb
    CONNECT_EXCEPTION = MySQLdb.OperationalError
    LOG.info('Using MySQLdb as the database module')
except ImportError:
    try:
        # .. if that fails, try with pymysql
        import pymysql as MySQLdb
        MySQLdb.install_as_MySQLdb()
        CONNECT_EXCEPTION = MySQLdb.err.OperationalError
        LOG.info('Using pymysql as the database module')
        if sys.version_info.major > 2:
            LOG.info('pymysql is known to be broken with Python 3. Consider '
                     'installing mysqlclient!')
    except ImportError:
        # if that fails, just set it to None to indicate that we have no db module
        MySQLdb = None  # pylint: disable=invalid-name
        LOG.info('Using cinfdata without database')


class CinfdataError(Exception):
    """Generic Cinfdata exception"""


class Cinfdata(object):
    """Class that provides easy access to the cinfdata database with optional local caching"""

    database_name = 'cinfdata'
    main_host = 'servcinf'
    main_port = '3306'
    secondary_host = '127.0.0.1'
    descriptions_table = 'dateplots_description'
    username = 'cinf_reader'
    password = 'cinf_reader'

    def __init__(self, setup_name, local_forward_port=9999, use_caching=False,
                 cache_dir=None, cache_only=False, log_level='INFO',
                 metadata_as_named_tuple=False):
        """Initialize local variables

        Args:
            setup_name (str): The setup name used as a table name prefix in the database.
                E.g. 'vhp' or 'stm312'.
            local_forward_port (int): The local port number that a port forwards to the
                database was created on. Default is 9999.
            use_caching (bool): If set to True, this module will locally cache data and
                metadata. WARNING: DO NOT use caching unless you understand the limitations.
            cache_dir (str): The directory to use for the cache. As default is used a
                directory named 'cache' in the same folder as this file (cinfdata.py) is
                located in
            cache_only (bool): If set to True, no connection will be formed to the database
            log_level (str): A string that indicates the log level, either 'INFO' (default)
                or 'DEBUG' for more output or 'DISABLE' to disable any further output

        .. warning:: Be careful with caching. It will keep returning the version of the
            data from the first time it was retrieved. If data is later added to the
            database or it is altered, the data that this module returns, when using
            caching will not reflect it.

        """
        # Setup logging
        if log_level == 'DEBUG':
            LOG.setLevel(logging.DEBUG)
        elif log_level == 'DISABLE':
            LOG.setLevel(logging.CRITICAL)

        # Init local variables
        self.setup_name = setup_name
        self.data_query = 'SELECT x, y FROM xy_values_{} WHERE measurement=%s '\
                          'ORDER BY id'.format(setup_name)
        self.metadata_query = 'SELECT * FROM measurements_{} WHERE id=%s'.format(setup_name)
        self._column_names = None

        # Init database connection
        self.connection = None
        self.cursor = None
        if MySQLdb is not None and not cache_only:
            self._init_database_connection(local_forward_port)

        # Init cache
        self.cache = None
        if use_caching:
            self.cache = Cache(cache_dir, setup_name)

        # Init the metadata named tuple (we need database for this)
        self._metadata_as_named_tuple = metadata_as_named_tuple
        if metadata_as_named_tuple:
            self._metadata_named_tuple = namedtuple('Metadata', self.column_names)

    def _init_database_connection(self, local_forward_port):
        """Initialize the database connection"""
        LOG.debug('Initialize database connection')
        try:
            self.connection = MySQLdb.connect(
                host=self.main_host, user=self.username, passwd=self.password,
                db=self.database_name,
            )
            LOG.info('Using direct db connection: cinfdata:3306')
        except CONNECT_EXCEPTION:
            try:
                self.connection = MySQLdb.connect(
                    host=self.secondary_host, port=local_forward_port,
                    user=self.username, passwd=self.password, db=self.database_name
                )
                LOG.info('Using port forward db connection: %s:%s', self.secondary_host,
                         local_forward_port)
            except CONNECT_EXCEPTION:
                self.connection = None
                LOG.info('No database connection')

        if self.connection is not None:
            self.cursor = self.connection.cursor()

    def get_data(self, measurement_id):
        """Get data for measurement_id"""
        # Check if this dataset is in the cache and if so return
        data = None
        if self.cache:
            data = self.cache.load_data(measurement_id)

        # Try and get the dataset from the database
        if data is None and self.cursor is not None:
            start = time()
            self.cursor.execute(self.data_query, measurement_id)
            data = np.array(self.cursor.fetchall())
            LOG.debug('Fetched data for id %s from database in %0.4e s', measurement_id,
                      time() - start)

            # If there was data in the db, possibly save to cache and return
            if data.size > 0:
                if self.cache:
                    self.cache.save_data(measurement_id, data)

        if data is None:
            error = 'No data found for id {}'.format(measurement_id)
            raise CinfdataError(error)

        return data

    def get_metadata(self, measurement_id):
        """Get metadata for measurement_id"""
        # Check if the metadata is in the cache
        metadata = None
        if self.cache:
            metadata = self.cache.load_metadata(measurement_id)

        # Try and get the metadata from the database
        if metadata is None and self.cursor is not None:
            # Get the data
            start = time()
            self.cursor.execute(self.metadata_query, measurement_id)
            metadata_raw = self.cursor.fetchall()
            LOG.debug('Fetched metadata for id %s from database in %0.4e s',
                      measurement_id, time() - start)

            # Raise error if there was not exactly 1 line
            if len(metadata_raw) != 1:
                raise CinfdataError('There was not exactly 1 row of metadata returned '
                                    'for id {}'.format(measurement_id))

            # Convert metadata to dict
            metadata = dict(zip(self.column_names, metadata_raw[0]))

            # Save in cache if present
            if self.cache:
                self.cache.save_metadata(measurement_id, metadata)

        # Raise error if we could not find any metadata
        if metadata is None:
            raise CinfdataError('No metadata found for id {}'.format(measurement_id))

        # Convert to namedtuple if requested
        if self._metadata_as_named_tuple:
            metadata = self._metadata_named_tuple(**metadata)

        return metadata

    @property
    def column_names(self):
        """Return the columns names from the measurements table"""
        # Note, this could be done cleverer with a lazy property implementation, but it
        # is more difficult to read
        if self._column_names is not None:
            return self._column_names

        # Check if the column names is in the cache
        if self.cache:
            column_names = self.cache.load_metadata('column_names')
            if column_names is not None:
                self._column_names = column_names
                return column_names

        # Try and get the column names from the database
        if self.cursor is not None:
            self.cursor.execute('DESCRIBE measurements_{}'.format(self.setup_name))
            column_names = [item[0] for item in self.cursor.fetchall()]
            self._column_names = column_names
            if self.cache:
                self.cache.save_metadata('column_names', column_names)
            return column_names

        raise CinfdataError('Column names not found')


class CinfdataCacheError(CinfdataError):
    """Exception for Cinfdata Cache related errors"""


class Cache(object):
    """Simple file base cache for cinf database loopkups"""

    def __init__(self, cache_dir, setup_name):
        """Initialize local variables"""
        if cache_dir is None:
            this_dir = path.dirname(path.abspath(__file__))
            self.cache_dir = path.join(this_dir, 'cache')
        else:
            self.cache_dir = cache_dir
        LOG.info('Using cache dir: %s', self.cache_dir)

        # Form folder paths, subfolder for each setup and under that subfolders for data
        # and metadata
        self.setup_dir = path.join(self.cache_dir, setup_name)
        self.data_dir = path.join(self.setup_dir, 'data')
        dirs = [self.cache_dir, self.setup_dir, self.data_dir]
        # Check permission on dirs and create them if possible
        self._check_and_create_dirs(dirs)

        # Form metadata file path and load if present
        self.metadata_file = path.join(self.setup_dir, 'metadata.pickle')
        if path.exists(self.metadata_file):
            error = None
            try:
                with open(self.metadata_file, 'rb') as file_:
                    self.metadata = cPickle.load(file_)
            except IOError:
                error = 'The file: {}\nwhich is needed for the cache, exists, but is '\
                        'not readable'
            except cPickle.UnpicklingError:
                error = 'Loading and interpreting the metadat file: {}\nfailed. '\
                        'Please report this as a bug.'
            if error is not None:
                raise CinfdataCacheError(error.format(self.metadata_file))
        else:
            self.metadata = {}

    @staticmethod
    def _check_and_create_dirs(dirs):
        """Check permissions of the cache directories and create them if necessayr"""
        # Check/create directories
        for dir_ in dirs:
            if path.exists(dir_):
                # If the path dir_ exists, check that it is a dir, and that it is read and
                # writeable
                error = None
                if not path.isdir(dir_):
                    error = 'The path: {}\nwhich is needed for the cache as a directory '\
                            'exists, but is not a directory'
                if not os.access(dir_, os.W_OK):
                    error = 'The directory: {}\nwhich is needed for the cache exists, '\
                            'but is not writeable'
                if not os.access(dir_, os.R_OK):
                    error = 'The directory: {}\nwhich is needed for the cache exists, '\
                            'but is not readable'
                if error is not None:
                    raise CinfdataCacheError(error.format(dir_))
            else:
                # If that path does not exist, create it
                try:
                    os.mkdir(dir_)
                except OSError:
                    error = 'Creation of the directory: {}\n which is neede for the '\
                            'cache failed. Please check permissions of the parent folder.'
                    raise CinfdataCacheError(error.format(dir_))

    def save_data(self, measurement_id, data):
        """Save a dataset to the cache

        Args:
            measurement_id (int): The database id of the dataset to save
            data (numpy.array): The data as a numpy array

        Returns:
            str: The file location of the saved array

        Raises:
            CinfdataCacheError: If data is an object array (a numpy array that contains
                generic Python objects)
        """
        start = time()
        filepath = path.join(self.data_dir, '{}.npy'.format(measurement_id))
        if data.dtype.hasobject:
            raise CinfdataCacheError('Saving object arrays is not supported')
        np.save(filepath, data)
        LOG.debug('Saved data for id %s to cache in %0.4e s', measurement_id, time() - start)
        return filepath

    def load_data(self, measurement_id):
        """Load a dataset from the cache

        Args:
            measurement_id (int): The database id of the dataset to load
        """
        start = time()
        # Form filepath and check if the file exists
        filepath = path.join(self.data_dir, '{}.npy'.format(measurement_id))
        if not path.exists(filepath):
            return None

        # Try and load the file and raise error is it fails
        try:
            data = np.load(filepath)
        except IOError:
            message = 'The cache file:\n{}\nexists, but could not be loaded. '\
                      'Check file permissions'
            raise CinfdataCacheError(message.format(filepath))
        LOG.debug('Loaded data for id %s from cache in %0.4e s', measurement_id,
                  time() - start)
        return data

    def save_metadata(self, key, metadata):
        """Save a metadata for a key to the cache

        .. note:: This function is used both to save metadata for measurements and other
            data that neede to be cached across script runs

        Args:
            key (int or str): The key to save the metadata under. This can either be the
                integer id of a measurements (e.g. 27431) or a text string for save other
                data (e.g. 'column_names')
            metadata (dict or list): The metadata to save under ``key``

        Raises:
            CinfdataCacheError: On problems saving the metadata to disk

        """
        start = time()
        self.metadata[key] = metadata
        self._save_metadatafile_to_file()
        LOG.debug('Saved metadata for key %s to cache in %0.4e s', key, time() - start)

    def _save_metadatafile_to_file(self):
        """Save the metadata dict to a file"""
        error = None
        try:
            with open(self.metadata_file, 'wb') as file_:
                cPickle.dump(self.metadata, file_)
        except IOError:
            error = 'The file: {}\nwhich is needed by the cache is not writable. '\
                    'Check the file permissions.'
        except cPickle.PickleError:
            error = 'Python was unable to save the metadata dict. Report this as a bug.'
        if error is not None:
            raise CinfdataCacheError(error)

    def load_metadata(self, key):
        """Load a meta dataset from the cache

        Args:
            key (int or str): The key to save the metadata under. This can either be the
                integer id of a measurements (e.g. 27431) or a text string for save other
                data (e.g. 'column_names')
        """
        start = time()
        metadata = self.metadata.get(key)
        if metadata is not None:
            LOG.debug('Loaded metadata for key %s from cache in %0.4e s', key, time() - start)
        return metadata


def run_module():
    """Run the module"""
    cinfdata = Cinfdata('dummy', use_caching=True, log_level='DEBUG',
                        metadata_as_named_tuple=True)
    data = cinfdata.get_data(26297)
    print(cinfdata.get_metadata(26297))
    from matplotlib import pyplot as plt
    plt.plot(data[:, 0], data[:, 1])
    plt.show()


if __name__ == '__main__':
    run_module()

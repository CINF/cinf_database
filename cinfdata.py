
from __future__ import unicode_literals, print_function
from os import path
import os
import sys


# The print function is needed for the MySQLdb imports, therefore it is defined before all
# the imports are complete
INHIBIT_OUTPUT = False
def print_message(message, logging=False):
    """Print a message to the user, using either simple prints or logging"""
    if INHIBIT_OUTPUT:
        return
    if logging:
        pass
    else:
        print('CINFDATA: {}'.format(message))


# First try and import MySQLdb ..
try:
    import MySQLdb
    CONNECT_EXCEPTION = MySQLdb.OperationalError
    print_message('Using MySQLdb as the database module')
except ImportError:
    try:
        # .. if that fails, try with MySQLdb
        import pymysql as MySQLdb
        MySQLdb.install_as_MySQLdb()
        CONNECT_EXCEPTION = MySQLdb.err.OperationalError
        print_message('Using pymysql as the database module')
        if sys.version_info.major > 2:
            print_message('pymysql is known to be broken with Python 3. Consider '
                          'installing mysqlclient!')
    except ImportError:
        # if that fails, just set it to None to indicate
        MySQLdb = None
        print_message('Using cinfdata without database')




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
                 cache_dir=None, cache_only=False):
        """Initialize local variables

        Args:
            setup_name (str): The setup name used as a table name prefix in the database.
                E.g. 'vhp' or 'stm312'.
            local_forward_port (int): The local port number that a port forwards to the
                database was created on. Default is 9999.
            use_caching (bool): If set to True, this module will locally cache data and
                metadata. WARNING: DO NOT use caching unless you understand the limitations.
            cache_dir (str): The directory to use for the cache. As default i used a
                directory named 'cache' in the same folder as this file (cinfdata.py) is
                located in
            cache_only (bool): If set to True, no connection will be formed to the database

        .. warning:: Be careful with caching. It will keep returning the version of the
            data from the first time it was retrieved. If data is later added to the
            database or it is altered, the data that this module returns, when using
            caching will not reflect it.

        """
        # Init local variables
        self.measurements_table = 'measurements_{}'.format(setup_name)
        self.xy_values_table = 'xy_values_{}'.format(setup_name)
        self.dateplots_table = 'dateplots_{}'.format(setup_name)

        # Init database connection
        self.connection = None
        self.cursor = None
        if MySQLdb is not None and not cache_only:
            self._init_database_connection(local_forward_port)

        # Init cache
        self.cache = None
        if use_caching:
            self.cache = Cache(cache_dir, setup_name)

    def _init_database_connection(self, local_forward_port):
        """Initialize the database connection"""
        try:
            self.connection = MySQLdb.connect(
                host=self.main_host, user=self.username, passwd=self.password,
                db=self.database_name,
            )
            print_message('Using direct db connection: cinfdata:3306')
        except CONNECT_EXCEPTION:
            try:
                self.connection = MySQLdb.connect(
                    host=self.secondary_host, port=local_forward_port,
                    user=self.username, passwd=self.password, db=self.database_name
                )
                print_message('Using port forward db connection: {}:{}'.format(self.secondary_host, local_forward_port))
            except CONNECT_EXCEPTION:
                self.connection = None
                print_message('No database connection')

        if self.connection is not None:
            self.cursor = self.connection.cursor()

    def get_data(measurement_id):
        pass

    def get_metadata(measurement_id):
        pass


class CinfdataCacheError(Exception):
    """Exception for Cinfdata Cache related errors"""


class Cache(object):
    """Simple file base cache for cinf database loopkups"""

    def __init__(self, cache_dir, setup_name):
        """Initialize local variables"""
        if cache_dir is None:
            this_dir = path.dirname(path.abspath(__file__))
            self.cache_dir = path.join(this_dir, 'cache')
        print_message('Cache dir: {}'.format(self.cache_dir))

        # Form folder paths, subfolder for each setup and under that subfolders for data
        # and metadata
        self.setup_dir = path.join(self.cache_dir, setup_name)
        self.data_dir = path.join(self.cache_dir, setup_name, 'data')
        self.metadata_dir = path.join(self.cache_dir, setup_name, 'metadata')
        dirs = [self.cache_dir, self.setup_dir, self.data_dir, self.metadata_dir]

        # Check/crate directories
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
                            'but us not writeable'
                if not os.access(dir_, os.R_OK):
                    error = 'The directory: {}\nwhich is needed for the cache exists, '\
                            'but us not readable'
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


def test():
    cinfdata = Cinfdata('dummy', use_caching=True, cache_only=True)


if __name__ == '__main__':
    test()

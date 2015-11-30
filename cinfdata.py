
from __future__ import unicode_literals
import sys

# First try and import MySQLdb ..
try:
    import MySQLdb
    CONNECT_EXCEPTION = MySQLdb.OperationalError
    print('CINFDATA: Using MySQLdb as the database module')
except ImportError:
    try:
        # .. if that fails, try with MySQLdb
        import pymysql as MySQLdb
        MySQLdb.install_as_MySQLdb()
        CONNECT_EXCEPTION = MySQLdb.err.OperationalError
        print('CINFDATA: Using pymysql as the database module')
        if sys.version_info.major > 2:
            print('CINFDATA: pymysql is known to be broken with Python 3. Consider '
                  'installing mysqlclient!')
    except ImportError:
        # if that fails, just set it to None to indicate
        MySQLdb = None
        print('CINFDATA: Using cinfdata without database')


class Cinfdata(object):
    """Class that provides easy access to the cinfdata database with optional local caching"""

    database_name = 'cinfdata'
    main_host = 'servcinf'
    main_port = '3306'
    secondary_host = 'localhost'
    descriptions_table = 'dateplots_description'
    username = 'cinf_reader'
    password = 'cinf_reader'

    def __init__(self, setup_name, local_forward_port=9999, use_caching=False, cache_dir=None):
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
        try:
            self.connection = MySQLdb.connect(
                host=self.main_host, user=self.username, passwd=self.password,
                db=self.database_name,
            )
            print('CINFDATA: Using direct db connection: cinfdata:3306')
        except CONNECT_EXCEPTION:
            try:
                self.connection = MySQLdb.connect(
                    host=self.secondary_host, port=local_forward_port,
                    user=self.username, passwd=self.password, db=self.database_name
                )
                print('CINFDATA: Using port forward db connection: {}:{}'.format(self.secondary_host, local_forward_port))
            except CONNECT_EXCEPTION:
                self.connection = None
                print('CINFDATA: No database connection')
        if self.connection is None:
            self.cursor = self.connection.cursor()

        # Init cache
        HERE
            


def test():
    cinfdata = Cinfdata('dummy')


if __name__ == '__main__':
    test()

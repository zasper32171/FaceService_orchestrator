import configparser
import pymysql

from collect import Collector


class ConfigReader():

    def __init__(self, path):

        self._parser = configparser.ConfigParser()
        self._parser.read(path)

    def init_db_instance(self):

        conf = self._parser['database']

        addr = conf.get('db_addr')
        port = conf.getint('db_port')
        user = conf.get('db_user')
        passwd = conf.get('db_passwd')
        schema = conf.get('db_schema')

        db = pymysql.connect(host=addr, port=port,
                             user=user, passwd=passwd, db=schema)
        return db

    def init_collector(self):

        db = self.init_db_instance()

        conf = self._parser['collector']

        addr = conf.get('collector_addr')
        port = conf.getint('collector_port')

        node_path = conf.get('node_path')

        collector = Collector(addr, port)
        collector.set_database(db)
        collector.add_nodes(node_path)

        return collector

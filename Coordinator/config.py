import configparser
import pymysql

from coordinate import Coordinator


class ConfigReader():

    def __init__(self, path):

        self._parser = configparser.ConfigParser()
        self._parser.read(path)

    def init_db_instance(self):

        conf = self._parser['database']

        addr   = conf.get('db_addr')
        port   = conf.getint('db_port')
        user   = conf.get('db_user')
        passwd = conf.get('db_passwd')
        schema = conf.get('db_schema')

        db = pymysql.connect(host=addr, port=port,
                             user=user, passwd=passwd, db=schema)
        return db

    def init_coordinator(self):

        db = self.init_db_instance()

        conf = self._parser['coordinator']

        node_path         = conf.get('node_path')
        handler_type_path = conf.get('handler_type_path')
        service_type_path = conf.get('service_type_path')

        coordinator = Coordinator()
        coordinator.set_database(db)
        coordinator.add_nodes(node_path)
        coordinator.add_handler_types(handler_type_path)
        coordinator.add_service_types(service_type_path)

        return coordinator

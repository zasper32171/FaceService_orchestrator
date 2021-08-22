import os
import threading
import json
import time
import requests


class Coordinator(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(
            self, daemon=True
        )

        self._db = None

        self._nodes    = []
        self._handlers = []
        self._services = []

        self._sessions = []

        self._terminating = False
        self._terminated  = threading.Event()

    def set_database(self, db):

        self._db = db

    def add_nodes(self, path):

        for file in os.listdir(path):

            file = os.path.join(path, file)

            if not os.path.isfile(file):

                continue

            try:
                self._nodes.append(json.load(open(file)))

            except Exception:

                pass

    def add_handler_types(self, path):

        for file in os.listdir(path):

            file = os.path.join(path, file)

            if not os.path.isfile(file):

                continue

            try:
                self._handlers.append(json.load(open(file)))

            except Exception:

                pass

    def add_service_types(self, path):

        for file in os.listdir(path):

            file = os.path.join(path, file)

            if not os.path.isfile(file):

                continue

            try:
                self._services.append(json.load(open(file)))

            except Exception:

                pass

    def get_node(self, node_id):

        result = [n for n in self._nodes if n['node_id'] == node_id]

        assert len(result) <= 1

        return result[0] if result else None

    def get_service_type(self, service_id):

        result = [s for s in self._services if s['service_id'] == service_id]

        assert len(result) <= 1

        return result[0] if result else None

    def get_handler_type(self, handler_id):

        result = [h for h in self._handlers if h['handler_id'] == handler_id]

        assert len(result) <= 1

        return result[0] if result else None

    def get_session(self, session_id):

        result = [s for s in self._sessions if s['session_id'] == session_id]

        assert len(result) <= 1

        return result[0] if result else None

    def init_session(self, session_id, service_id):

        if self.get_session(session_id) is not None:

            raise Exception

        service = self.get_service_type(service_id)

        if service is None:

            raise Exception

        for t in service['template']:

            node = self.get_node(t['node_id'])

            url = 'http://' + node['node_addr'] + ':' + str(node['node_port'])

            payload = {
                'action':     'init',
                'session_id': session_id,
                'blueprint':  t['blueprint']
            }

            response = requests.post(url, data=json.dumps(payload))

            if not response.json()['result'] == 'Succeeded':

                raise Exception

        self._sessions.append(
            {
                'session_id': session_id,
                'node_list':  [t['node_id'] for t in service['template']],
                'status':     'initialized'
            }
        )

    def start_session(self, session_id):

        s = self.get_session(session_id)

        if s is None:

            raise Exception

        for node_id in s['node_list']:

            node = self.get_node(node_id)

            url = 'http://' + node['node_addr'] + ':' + str(node['node_port'])

            payload = {
                'action':     'start',
                'session_id': session_id
            }

            response = requests.post(url, data=json.dumps(payload))

            if not response.json()['result'] == 'Succeeded':

                raise Exception

        s['status'] = 'running'

    def stop_session(self, session_id):

        s = self.get_session(session_id)

        if s is None:

            raise Exception

        for node_id in s['node_list']:

            node = self.get_node(node_id)

            url = 'http://' + node['node_addr'] + ':' + str(node['node_port'])

            payload = {
                'action':     'stop',
                'session_id': session_id
            }

            response = requests.post(url, data=json.dumps(payload))

            if not response.json()['result'] == 'Succeeded':

                raise Exception

        s['status'] = 'terminated'

    def delete_session(self, session_id):

        s = self.get_session(session_id)

        if s is None:

            raise Exception

        for node_id in s['node_list']:

            node = self.get_node(node_id)

            url = 'http://' + node['node_addr'] + ':' + str(node['node_port'])

            payload = {
                'action':     'delete',
                'session_id': session_id
            }

            response = requests.post(url, data=json.dumps(payload))

            if not response.json()['result'] == 'Succeeded':

                raise Exception

        self._sessions.remove(s)

    def run(self):

        try:
            cursor = self._db.cursor()

            self.init_session(0, 0)
            time.sleep(5)

            self.start_session(0)
            time.sleep(5)

            self.stop_session(0)
            time.sleep(5)

            self.delete_session(0)

            while not self._terminating:

                time.sleep(0.5)

        finally:

            self._terminating = False
            self._terminated.set()

    def stop(self):

        self._terminating = True
        self._terminated.wait()

        if self._db is not None:
            self._db.close()

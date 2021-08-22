import http.server
import threading
import json
import os
import pymysql


class CollectorRequestHandler(http.server.SimpleHTTPRequestHandler):

    def process_request(self, data):

        # Preprocessing

        client_addr = self.client_address[0]
        node = self.server.get_node_by_addr(client_addr)

        assert node is not None

        try:
            for sys_info in data['sys_info']:

                sys_info['node_id'] = node['node_id']

                # TODO: suppprt multi-GPU
                if sys_info['gpu_info']:
                    sys_info.update(sys_info['gpu_info'][0])

                sys_info.pop('gpu_info', None)
                sys_info.pop('gpu_id', None)

            for proc_info in data['proc_info']:

                # TODO: suppprt multi-GPU
                if proc_info['gpu_info']:
                    proc_info.update(proc_info['gpu_info'][0])

                proc_info.pop('gpu_info', None)
                proc_info.pop('gpu_id', None)

        except KeyError as e:

            response = {'result': 'Failed',
                        'reason': '%s: %s' % (type(e).__name__, e)}

        # Database Insertion

        db = self.server.get_database()
        cursor = db.cursor()

        try:
            for info_type in data.keys():

                for info in data[info_type]:

                    cursor.execute(
                        'INSERT INTO %s (%s) VALUES (%s)' % (
                            info_type,
                            ', '.join([item[0] for item in info.items()]),
                            ', '.join(['%s'] * len(info))
                        ), [item[1] for item in info.items()]
                    )

            db.commit()

        except (KeyError, pymysql.MySQLError) as e:

            response = {'result': 'Failed',
                        'reason': '%s: %s' % (type(e).__name__, e)}
        else:
            response = {'result': 'Succeeded'}

        return response

    def do_POST(self):

        length = int(self.headers['content-length'])

        try:
            data = json.loads(self.rfile.read(length).decode())

        except json.JSONDecodeError as e:

            response = {'result': 'Failed',
                        'reason': '%s: %s' % (type(e).__name__, e)}
        else:
            response = self.process_request(data)

        # TODO: different response code
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(response).encode())


class Collector(http.server.HTTPServer, threading.Thread):

    def __init__(self, addr, port):

        http.server.HTTPServer.__init__(
            self, (addr, port),
            CollectorRequestHandler
        )

        threading.Thread.__init__(
            self, target=self.serve_forever,
            daemon=True
        )

        self._db = None

        self._nodes = []

    def set_database(self, db):

        self._db = db

    def get_database(self):

        return self._db

    def add_nodes(self, path):

        for file in os.listdir(path):

            file = os.path.join(path, file)

            if not os.path.isfile(file):

                continue

            try:
                self._nodes.append(json.load(open(file)))

            except Exception:

                pass

    def get_node_by_addr(self, addr):

        result = [n for n in self._nodes if n['node_addr'] == addr]

        assert len(result) <= 1

        return result[0] if result else None

    def stop(self):

        self.shutdown()

        if self._db is not None:
            self._db.close()

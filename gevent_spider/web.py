import gevent
from gevent.pywsgi import WSGIServer
from gevent import sleep
from geventwebsocket.handler import WebSocketHandler
import json
import os
import subprocess
gevent.monkey.patch_all()

class Client(object):
    def __init__(self, websocket, env):
        self.ws = websocket
        self.env = env
    def send(self, message):
        self.ws.send(json.dumps(message))
    def receive(self):
        data = self.ws.receive()
        try:
            json_data = json.loads(data)
        except Exception, e:
            print data
            print "JSON Error: %s" % e
            return None
        return json_data
    def send_status(self, message, id=None):
        self.send({'cmd': 'status', 'status': message, 'id': id})
    def send_result(self, result):
        self.send({'cmd': 'result', 'result': result})

def tail_f(file):
    count = 0
    interval = 1.0

    while True:
        if count > 10:
            return
        where = file.tell()
        line = file.readline()
        if not line:
            count += 1
            sleep(interval)
            file.seek(where)
        else:
            yield line

def application(env, start_response):
    websocket = env.get('wsgi.websocket')

    if not websocket:
        return http_handler(env, start_response)

    client = Client(websocket, env)

    while True:
        message = client.receive()
        cmd = message['cmd']
        id = message['id']
        if cmd == 'tail':
            line = 0
            #Main Loop
            file = message['url']
            try:
                user_file = open(file, 'r')
                for line in tail_f(user_file):
                    client.send_status(line, id=id)
            except Exception, e:
                print "ERROR: %s" % e

def http_handler(env, start_response):
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        yield open(os.path.join(os.path.dirname(__file__), 'media/index.html'), 'r').read()
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        yield '<h1>Not Found</h1>'

def serve():
    WSGIServer(('', 8088), application, handler_class=WebSocketHandler).serve_forever()

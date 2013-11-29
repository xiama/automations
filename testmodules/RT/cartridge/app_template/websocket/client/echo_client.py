# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient

class EchoClient(WebSocketClient):
    def opened(self):
        def data_provider():
            for i in range(3):
                yield "%d-linux is good\n" % (i)
                
        self.send(data_provider())

    def closed(self, code, reason):
        print(("Closed down", code, reason))

    def received_message(self, m):
        print("=> %d %s" % (len(m), str(m)))
        self.close(reason='Bye bye')

if __name__ == '__main__':
    try:
        ws = EchoClient('ws://localhost:9000/ws/', protocols=['http-only', 'chat'])
        ws.daemon = False
        ws.connect()
    except KeyboardInterrupt:
        ws.close()

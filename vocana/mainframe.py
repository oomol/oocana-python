import zmq
import json

class Mainframe:

    def __init__(self, address: str) -> None:
        self.address = address
        context = zmq.Context()
        self.sock = context.socket(zmq.REQ)
    
    def connect(self):
        self.sock.connect(self.address)
   
    def send(self, msg):
        self.sock.send_json(msg)

    def recv(self):
        return self.sock.recv()

    def send_ready(self, msg):
        self.send(msg)
        messageBytes = self.sock.recv()
        return json.loads(messageBytes)
    
    def disconnect(self):
        self.sock.disconnect(self.address)
